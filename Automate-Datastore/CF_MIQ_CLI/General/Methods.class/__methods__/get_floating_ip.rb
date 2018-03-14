#
# Description: Get/Create Free Floating IP for given
#      Tenant and network.
#
# Input:
# cloud_tenant_id (integer) required = Cloud tenant id
# cloud network_id (integer) required = Cloud network id
# count (integer) optional = Number of Floating IPs requesting
# 
# Returned list of ips and ids

begin
  def log(level, msg)
    @method = 'allocateFloatingIP'
    $evm.log(level, "#{@method}: #{msg}")
  end
  
  def log_err(err)
    log(:error, "#{err.class} #{err}")
    log(:error, "#{err.backtrace.join("\n")}")
  end
  
  def get_fog_object(ext_mgt_system, type="Compute", tenant="admin", auth_token=nil, encrypted=false, verify_peer=false)
    proto = "https"
    require 'fog/openstack'

    begin
      return Object::const_get("Fog").const_get("#{type}").new({
        :provider => "OpenStack",
        :openstack_api_key => ext_mgt_system.authentication_password,
        :openstack_username => ext_mgt_system.authentication_userid,
        :openstack_auth_url => "#{proto}://#{ext_mgt_system.hostname}:#{ext_mgt_system.port}/v2.0/tokens",
        #:openstack_auth_token => auth_token,
        :connection_options => { :ssl_verify_peer => verify_peer },
        :openstack_tenant => tenant
      })
        
    rescue Excon::Errors::SocketError => sockerr
      raise unless sockerr.message.include?("end of file reached (EOFError)")
      log(:error, "Looks like potentially an ssl connection due to error: #{sockerr}")
      return get_fog_object(ext_mgt_system, type, tenant, auth_token, true, verify_peer)
    rescue => loginerr
      log(:error, "Error logging [#{ext_mgt_system}, #{type}, #{tenant}, #{auth_token rescue "NO TOKEN"}]")
      log_err(loginerr)
      log(:error, "Returning nil")
    end
    return nil
  end  

  def list_external_networks(conn)
    array = []
    networks = conn.list_networks.body
    log(:info, "Networks: #{networks.inspect}")
    for network in networks["networks"]
      array.push(network) if network["router:external"]
    end
    return array
  end

  if ($evm.object['count'].nil? or $evm.object['count'].blank?)
      count = 1
  else
      count = Integer($evm.object['count'])
  end

  if (count<=0)
      raise ArgumentError, "count must be positive integer"
  end

  floating_network = $evm.vmdb(:cloud_network).find_by_id($evm.object['cloud_network_id']).name
  log(:info, "Floating Network Name: #{floating_network}")

  ip_list = {}

  log(:info, "Create Floating IP/IPs")
  require 'fog/openstack'

  log(:info, "Object Type: #{$evm.root['vmdb_object_type']}")
  tenant_name = $evm.vmdb(:cloud_tenant).find_by_id($evm.object['cloud_tenant_id']).name
  ext_management_system = $evm.vmdb(:cloud_tenant).find_by_id($evm.object['cloud_tenant_id']).ext_management_system

  log(:info, "Connecting to tenant #{tenant_name}")

  conn = get_fog_object(ext_management_system, "Compute", tenant_name, encrypted=true)

  log(:info, "Have Compute connection #{conn.class} #{conn.inspect}")

  netconn = get_fog_object(ext_management_system, "Network", tenant_name, encrypted=true)

  log(:info, "Have Network connection #{netconn.class} #{netconn.inspect}")

  pool_name = floating_network
  pool_name = list_external_networks(netconn).first["name"] if pool_name.nil?

  log(:info, "Allocating IP/IPs from #{pool_name}")

  addresses = []
  while (count > 0)
      address = conn.allocate_address(pool_name).body
      log(:info, "Allocated #{address['floating_ip'].inspect}")

      addresses << address
      count = count - 1
  end

  ext_management_system.refresh

  # Set timer 10 min. (600 seconds)
  timer = 600
  new_ip = nil

  for address in addresses
      while (timer > 0)
          # Get Floating IP data
          new_ips = $evm.vmdb(:floating_ip).where(["cloud_network_id = ? and
                                             cloud_tenant_id = ? and
                                             address = ? and status = ? and
                                             vm_id is NULL",
                                             $evm.object['cloud_network_id'],
                                             $evm.object['cloud_tenant_id'],
                                             address['floating_ip']['ip'],
                                             "DOWN"])
     
          # Have data done
          if new_ips and new_ips.length > 0
              log(:info, "Time: #{600 - timer} seconds - Number of IPs: #{new_ips.length}")
              log(:info, "Floating IPs: #{new_ips.inspect}")
              new_ip = new_ips[0]
              break
          end
      
          # Wait 5 seconds, count down and continue
          sleep(5)
          timer = timer - 5

          # Raise error if taking to long to get data
          raise 'ERROR: Timeout getting created floating IP information' if timer <=0
      end

      log(:info, "Floating IP: #{address['floating_ip']['ip']} ID: #{new_ip.id}")
      ip_list[address['floating_ip']['ip']] = new_ip.id 

      log(:info, "ip #{ip_list}")

  end
  
  # For automation_task set return data. status and return data
  # List of IP's and their IDs
  case $evm.root['vmdb_object_type'] 
    when 'automation_task'
      automation_request = $evm.root['automation_task'].automation_request
      automation_request.set_option(:return, JSON.generate({:status => 'success',
                                                              :return => ip_list}))
  end
  exit MIQ_OK
    
rescue => err
  log(:error, "[#{err}]\n#{err.backtrace.join("\n")}")
  case $evm.root['vmdb_object_type'] 
    when 'automation_task'
      automation_request = $evm.root['automation_task'].automation_request
      automation_request.set_option(:return, JSON.generate({:status => 'error',
                                                              :return => "[#{err}]\n#{err.backtrace.join("\n")}"}))
  end  
  exit MIQ_ABORT
end
