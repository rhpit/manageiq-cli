# Description: Replease Floating IP
# Input - Floating IP either by ID or Name, not both
# floating_ip (string)     = "10.8.240.201"
# floating_ip_id (integer) = 2017000000000002
#
#

begin
  def log(level, msg)
    @method = 'release_floating_ip'
    $evm.log(level, "#{@method}: #{msg}")
  end
  
  def log_err(err)
    log(:error, "#{err.class} #{err}")
    log(:error, "#{err.backtrace.join("\n")}")
  end
  
  def get_fog_object(ext_mgt_system, type="Compute", tenant="admin", auth_token=nil, encrypted=false, verify_peer=false)
    proto = "https"
    #proto = "http" if encrypted == false
    require 'fog/openstack'

    begin
      return Object::const_get("Fog").const_get("#{type}").new({
        :provider => "OpenStack",
        :openstack_api_key => ext_mgt_system.authentication_password,
        :openstack_username => ext_mgt_system.authentication_userid,
        :openstack_auth_url => "#{proto}://#{ext_mgt_system.hostname}:#{ext_mgt_system.port}/v2.0/tokens",
        #:openstack_auth_token => unless auth_token.nil? or auth_token == 0,
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

  def list_external_addresses(conn, input_ip)
    ip = nil
    addresses = conn.list_all_addresses.body
    for address in addresses["floating_ips"]
      ip = address if address["ip"] == input_ip.name
    end
    log(:info, "Address: #{ip}")
    return ip
  end
  
  log(:info, "Release Floating IP")
  ip = nil
  
  if $evm.object['floating_ip'] and $evm.object['floating_ip_id']
    raise ArgumentError, 'To many arguments given - 1 expected'  
  end

  if ($evm.object['floating_ip_id'].nil? or $evm.object['floating_ip_id'].blank?) and 
     ($evm.object['floating_ip'].nil? or $evm.object['floating_ip'].blank?)
    raise ArgumentError, 'No input argument supplied. Expected 1.'
  end
  
  ip = $evm.vmdb(:floating_ip).find_by_id($evm.object['floating_ip_id']) if $evm.object['floating_ip_id']
  ip = $evm.vmdb(:floating_ip).find_by_name($evm.object['floating_ip']) if $evm.object['floating_ip']

  raise 'Floating IP not found' if ip == nil

  log(:info, "Floating IP #{ip.name}")
  
  ext_network = $evm.vmdb(:cloud_network).find_by_id(ip.cloud_network_id).name
  log(:info, "External Network #{ext_network}")
    
  require 'fog/openstack'

  log(:info, "Object Type: #{$evm.root['vmdb_object_type']}")
  
  tenant_name = $evm.vmdb(:cloud_tenant).find_by_id(ip.cloud_tenant_id).name
  ext_management_system = $evm.vmdb(:cloud_tenant).find_by_id(ip.cloud_tenant_id).ext_management_system

  log(:info, "Connecting to tenant #{tenant_name}")

  conn = get_fog_object(ext_management_system, "Compute", tenant_name, encrypted=true)

  log(:info, "Have Compute connection #{conn.class} #{conn.inspect}")

  log(:info, "Releasing IP #{ip.name}")

  address = list_external_addresses(conn, ip)
  log(:info, "Address #{address}")
  
  raise '(Openstack) Floating IP not found' if address == nil
    
  response = conn.release_address(address["id"])
  
  log(:info, "Release Result #{response.status}")
  log(:info, "Release Inspection #{response.body}")
  
  # For automation_task set return data. status and return data
  # List of IP's and their IDs
  case $evm.root['vmdb_object_type'] 
    when 'automation_task'
      automation_request = $evm.root['automation_task'].automation_request
      automation_request.set_option(:return, JSON.generate({:status => response.status,
                                                              :return => response.body}))
  end
  ext_management_system.refresh

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
