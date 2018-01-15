# Description: Allocate and associate a new floating IP to a VM.
# Input - VM (required) - Either by name or ID
#         vm_name (string)   =   vm/instance name
#         vm_id  (integer)   =   vm/instance id
#         Floating Network (Optional) - Will pick the first available if not given
#         floating_network (string)  = Extternal Network Name   
#
begin

  def log(level, msg)
    @method = 'allocateFloatingIP'
    $evm.log(level, "#{@method}: #{msg}")
  end 

  def dump_root()
    log(:info, "Root:<$evm.root> Begin $evm.root.attributes")
    $evm.root.attributes.sort.each { |k, v| log(:info, "Root:<$evm.root> Attribute - #{k}: #{v}")}
    log(:info, "Root:<$evm.root> End $evm.root.attributes")
    log(:info, "")
  end

  # Error logging convenience
  def log_err(err)
    log(:error, "#{err.class} #{err}")
    log(:error, "#{err.backtrace.join("\n")}")
  end

  def get_fog_object(ext_mgt_system, type="Compute", tenant="admin", encrypted=false, auth_token=nil, verify_peer=false)
    proto = "https"
    proto = "http" if encrypted == false
    require 'fog/openstack'
    
    begin
      return Object::const_get("Fog").const_get("#{type}").new({
        :provider => "OpenStack",
        :openstack_api_key => ext_mgt_system.authentication_password,
        :openstack_username => ext_mgt_system.authentication_userid,
        :openstack_auth_url => "#{proto}://#{ext_mgt_system.hostname}:#{ext_mgt_system.port}/v2.0/tokens",
        #:openstack_auth_token => auth_token unless auth_token.nil? or auth_token == 0,
        :connection_options => { :ssl_verify_peer => verify_peer },
        :openstack_tenant => tenant
        })
      
    rescue Excon::Errors::SocketError => sockerr
      raise unless sockerr.message.include?("end of file reached (EOFError)")
      log(:error, "Looks like potentially an ssl connection due to error: #{sockerr}")
      return get_fog_object(ext_mgt_system, type, tenant, true, auth_token, verify_peer)
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

  log(:info, "Begin Automate Method")
  vm = nil
  
  if $evm.object['vm_name'] and $evm.object['vm_id']
    raise ArgumentError, 'To many VM arguments given - Specify VM by Name or ID not both'  
  end

  if ($evm.object['vm_id'].nil? or $evm.object['vm_id'].blank?) and
     ($evm.object['vm_name'].nil? or $evm.object['vm_name'].blank?)
    raise ArgumentError, 'No VM input argument supplied.'
  end
  
  vm = $evm.vmdb(:vm).find_by_id($evm.object['vm_id']) if $evm.object['vm_id']
  vm = $evm.vmdb(:vm).find_by_name($evm.object['vm_name']) if $evm.object['vm_name']

  raise 'VM Instance not found' if vm == nil
  
  log(:info, "VM: #{vm.name}")
  
  dump_root

  floating_network = $evm.object['floating_network']
  log(:info, "floating_network: #{floating_network}")

  require 'fog/openstack'

  log(:info, "Found VM: #{vm.inspect}")
  log(:info, "Nova UUID for vm is #{vm.ems_ref}")

  tenant_name = $evm.vmdb(:cloud_tenant).find_by_id(vm.cloud_tenant_id).name

  log(:info, "Connecting to tenant #{tenant_name}")

  conn = get_fog_object(vm.ext_management_system, "Compute", tenant_name, true)

  log(:info, "Have Compute connection #{conn.class} #{conn.inspect}")

  netconn = get_fog_object(vm.ext_management_system, "Network", tenant_name, true)

  log(:info, "Have Network connection #{netconn.class} #{netconn.inspect}")

  pool_name = floating_network
  pool_name = list_external_networks(netconn).first["name"] if pool_name.nil?

  log(:info, "Allocating IP from #{pool_name}")

  address = conn.allocate_address(pool_name).body
  log(:info, "Allocated #{address['floating_ip'].inspect}")

  res = conn.associate_address("#{vm.ems_ref}", "#{address['floating_ip']['ip']}")
  log(:info, "Associate: Response: #{res.inspect}")
  vm.custom_set("NEUTRON_floating_ip", "#{address['floating_ip']['ip']}")
  vm.custom_set("NEUTRON_floating_id", "#{address['floating_ip']['id']}")
  vm.refresh

  res_ip = {}
  res_ip[address['floating_ip']['ip']] = address['floating_ip']['id']
  log(:info, "End Automate Method")
  
  # For automation_task set return data. status and return data
  # List of IP's and their IDs
  case $evm.root['vmdb_object_type'] 
    when 'automation_task'
      automation_request = $evm.root['automation_task'].automation_request
      automation_request.set_option(:return, JSON.generate({:status => res.status,
                                                              :return => res_ip}))
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
