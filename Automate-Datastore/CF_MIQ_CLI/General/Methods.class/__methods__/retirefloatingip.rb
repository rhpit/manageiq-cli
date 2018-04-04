# Description: Retire all floating IP addresses from this machine.
# Input - VM (required) - Either by Name or ID
#         vm_name           (string)  =  vm/instance name
#         vm_id             (integer) =  vm/instance id
#         Cloud provider (optional) - Either by name or ID
#         cloud_provider    (string)  =  provider name
#         cloud_provider_id (integer) =  provider id 
#         Coud network   (optional) - Either by name or ID
#         cloud network     (string)  =  network name
#         cloud_network_id  (integer) =  network id
#         cloud tenant   (optional) - Either by name or ID
#         cloud_tenant      (string)  =  tenant name
#         cloud_tenant_id   (integer) =  tenant id


begin

  # Logger
  def log(level, msg)
    $evm.log(level, "#{msg}")
  end 

   # Error logging convenience
  def log_err(err)
    log(:error, "#{err.class} #{err}")
    log(:error, "#{err.backtrace.join("\n")}")
  end

  def dump_root()
    log(:info, "Root:<$evm.root> Begin $evm.root.attributes")
    $evm.root.attributes.sort.each { |k, v| log(:info, "Root:<$evm.root> Attribute - #{k}: #{v}")}
    log(:info, "Root:<$evm.root> End $evm.root.attributes")
    log(:info, "")
  end

  def get_fog_object(ext_mgt_system, type="Compute", tenant="admin",
                     encrypted=false, auth_token=nil, verify_peer=false)
    proto = "https"
    proto = "http" if encrypted == false
    require 'fog/openstack'
    begin
      return Object::const_get("Fog").const_get("#{type}").new({
        :provider => "OpenStack",
        :openstack_api_key => ext_mgt_system.authentication_password,
        :openstack_username => ext_mgt_system.authentication_userid,
        :openstack_auth_url => "#{proto}://#{ext_mgt_system.hostname}:#{ext_mgt_system.port}/v2.0/tokens",
        #:openstack_auth_token => auth_token,
        :connection_options => { :ssl_verify_peer => verify_peer,
                                 :ssl_version => :TLSv1 },
        :openstack_tenant => tenant
        })
    rescue Excon::Errors::SocketError => sockerr
      raise unless sockerr.message.include?("end of file reached (EOFError)")
      log(:error,
          "Looks like potentially an ssl connection due to error: #{sockerr}")
      return get_fog_object(ext_mgt_system, type, tenant, true,
                            auth_token, verify_peer)
    rescue => loginerr
      log(:error, "Error logging [#{ext_mgt_system}, #{type}, #{tenant}, #{auth_token rescue "NO TOKEN"}]")
      log_err(loginerr)
      log(:error, "Returning nil")
    end
    return nil
  end  

  log(:info, "Begin Automate Method Retire Floating IP ")
  vm = nil

  # Validate parameters  
  # Check for VM input
  if $evm.object['vm_name'] and $evm.object['vm_id']
    raise ArgumentError, 'To many VM arguments given - Specify VM by Name or ID, not both'  
  end

  # Check for Cloud Provider input
  if $evm.object['cloud_provider'] and $evm.object['cloud_provider_id']
      raise ArgumentError, 'To many Cloud Provider arguments given - Specify Cloud Provider by Name or ID, not both'
  end
  
  # Check for Cloud Network input
  if $evm.object['cloud_network'] and $evm.object['cloud_network_id']
    raise ArgumentError, 'To many Extenal Cloud Network arguments given - Specify External Cloud Network by Name or ID, not both'
  end

  # Check for Tenant input
  if $evm.object['cloud_tenant'] and $evm.object['cloud_tenant_id']
    raise ArgumentError, 'To many Cloud Tenant arguments given - Specify Tenant by Name or ID, not both'
  end
 
  # Check for VM Input - Required
  if ($evm.object['vm_id'].nil? or $evm.object['vm_id'].blank?) and
     ($evm.object['vm_name'].nil? or $evm.object['vm_name'].blank?)
    raise ArgumentError, 'No VM input argument supplied.'
  end

  # Get EMS ID
  ems_id = $evm.object['cloud_provider_id'] if $evm.object['cloud_provider_id']
  ems_id = $evm.vmdb(:ext_management_system).find_by_name($evm.object['cloud_provider']).id if $evm.object['cloud_provider']
  log(:info, "Provider ems_id: #{ems_id}")

  # Get VM by ID. 
  vm = $evm.vmdb(:vm).find_by_id($evm.object['vm_id']) if $evm.object['vm_id']

  # Get VM by name and other args given by ID
  vm_list = []
  cond_list = []
  where_str = ""
  if $evm.object['vm_name']
    # Build Where string
    where_str, cond_list = "name = ?", cond_list.push($evm.object['vm_name'])
    where_str, cond_list = where_str + " and ems_id = ?", cond_list.push(ems_id) if ems_id
    where_str, cond_list = where_str + " and cloud_tenant_id = ?", cond_list.push($evm.object['cloud_tenant_id']) if $evm.object['cloud_tenant_id']

    cond_list.insert(0, where_str)
    vm_list = $evm.vmdb(:vm).where(cond_list)

    log(:info, "cond_list: #{cond_list.inspect}")
    log(:info, "vm_list: #{vm_list.inspect}")

    # Handle cloud network
    if $evm.object['cloud_network_id']
      vms = []
      vm_list.each { |f| $evm.vmdb(:cloud_network).find_by_id(
                     $evm.object['cloud_network_id']).vms.each {
                         |g| vms << g if g.id == f.id
                     }}
      vm_list = vms
    end
  end

  log(:info, "vm_list: #{vm_list.inspect}")

  # Get VM by Name and othe args supplied by Name
  # Names are not unique so may have more than one.
  vms = []
  if vm_list && vm_list.length > 1 && ($evm.object['cloud_network'] ||
                                       $evm.object['cloud_tenant'])
    vm_list.each { |f| $evm.vmdb(:cloud_network).find_by_name(
                     $evm.object['cloud_network']).vms.each {
                         |g| vms << g if g.id == f.id and
                         f.cloud_tenant_id and
                         $evm.object['cloud_tenant'].equal?($evm.vmdb(
                         :cloud_tenant).find_by_id(f.cloud_tenant_id).name)
                     }
                 } if $evm.object['cloud_network'] && $evm.object['cloud_tenant']

    vm_list.each { |f| $evm.vmdb(:cloud_network).find_by_name(
                     $evm.object['cloud_network']).vms.each {
                         |g| vms << g if g.id == f.id
                     }} if $evm.object['cloud_network'] &&
                          $evm.object['cloud_tenant'].nil?

    vm_list.each { |f| vms << f if f.cloud_tenant_id and
                     $evm.object['cloud_tenant'] == 
                     $evm.vmdb(:cloud_tenant).find_by_id(f.cloud_tenant_id).name
                 } if $evm.object['cloud_network'].nil? &&
                      $evm.object['cloud_tenant']

    log(:info, "vms: #{vms.inspect}")
    vm_list = vms
  end

  log(:info, "vm_list: #{vm_list.inspect}")
  if vm_list &&  vm_list.length > 1 
    raise "ERROR: Multiple Instances with name #{$evm.object['vm_name']} - Supply provider, external network and/or tenant to narrow selection"
  else
    if vm_list
      vm = vm_list[0]
    end
  end

  raise 'VM Instance not found' if vm == nil
  
  log(:info, "VM: #{vm.name}")
  
  dump_root

  require 'fog/openstack'

  log(:info, "Found VM: #{vm.inspect}")
  log(:info, "Nova UUID for vm is #{vm.ems_ref}")
  log(:info, "ext_management_system: #{vm.ext_management_system.inspect}")
  log(:info, "ip addresses: #{vm.ipaddresses.inspect}")
  tenant_name = $evm.vmdb(:cloud_tenant).find_by_id(vm.cloud_tenant_id).name
  log(:info, "tenant name is #{tenant_name}")

  conn = get_fog_object(vm.ext_management_system, "Compute", tenant_name, true)
  netconn = get_fog_object(vm.ext_management_system, "Network", tenant_name, true)

  server_details = conn.get_server_details(vm.ems_ref).body['server']
  log(:info, "OpenStack server details: #{server_details.inspect}")
  addresses = server_details['addresses']

  release_addrs = []
  addresses.each_pair { |network, details|
    for address in details
       if address['OS-EXT-IPS:type'] == "floating"
          log(:info, "Found floating addr #{address.inspect}")
          release_addrs.push("#{address['addr']}")
       end
    end
  }

  res_retire = {}
  res_retire_success = true
  for addr in release_addrs
    log(:info, "Reclaiming: #{addr}")
    # must get the floating id from neutron
    floating = netconn.list_floating_ips.body['floatingips']
    for ip in floating
      if ip['floating_ip_address'] == "#{addr}"
         id = ip['id']
         log(:info, "Floating ID for #{addr} is #{id}")
         begin
           netconn.disassociate_floating_ip(id)
           log(:info, "Disassociated #{addr}")
           netconn.delete_floating_ip(id)
           log(:info, "Reclaimed #{addr}")
           res_retire[addr] = "Released"
         rescue => neutronerr
           log(:error, "Error reclaiming #{addr} #{neutronerr}\n#{neutronerr.backtrace.join("\n")}")
           res_retire[addr] = "Error reclaiming #{addr} #{neutronerr}\n#{neutronerr.backtrace.join("\n")}"
           res_retire_success = false
         end
      end
    end
  end

  vm.custom_set("NEUTRON_floating_id", nil)
  vm.custom_set("NEUTRON_floating_ip", nil)
  vm.refresh
  
  if res_retire_success == false
     raise "Failure Disassociating and Releasing Floating IP"
  end
  
  # For automation_task set return data. status and return data
  # List of IP's and their IDs
  case $evm.root['vmdb_object_type'] 
    when 'automation_task'
      automation_request = $evm.root['automation_task'].automation_request
      automation_request.set_option(:return, JSON.generate({:status => 'success',
                                                              :return => res_retire}))
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
