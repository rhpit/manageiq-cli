#
# Description: Obtain Floating IP/IPS for given
#      Tenant and External network.
# Cloud tenant                Either by name or ID
# cloud_tenant     (string)   pit-jenkins
# cloud_tenent_id  (integer)  2017000000000001
# Cloud network               External Network Either by name or ID
# cloud_network    (string)   10.8.240.0
# cloud_network_id (integer)  2017000000000002
# Floating IP                 Either by name of ID
# fip              (string)   10.8.240.33
# fip_id           (integer)  2017000000000145
# Returned list of ips, ids, and instance
#
begin
  def log(level, msg)
    @method = 'list_floating_ips'
    $evm.log(level, "#{@method}: #{msg}")
  end

  def log_err(err)
    log(:error, "#{err.class} #{err}")
    log(:error, "#{err.backtrace.join("\n")}")
  end

  log(:info, "List Floating IP/IPS")

  if $evm.object['cloud_network'] and $evm.object['cloud_network_id']
    raise ArgumentError, 'To many arguments given - Specify Floating IP External Network by Name or ID not both'
  end

  if $evm.object['cloud_tenant'] and $evm.object['cloud_tenant_id']
    raise ArgumentError, 'To many arguments given - Specify Cloud Tenant by Name or ID not both'
  end

  if $evm.object['fip'] and $evm.object['fip_id']
    raise ArgumentError, 'To many arguments given - Specify Floating IP by Name or ID not both'
  end

  $evm.object['cloud_tenant_id'] = $evm.vmdb(:cloud_tenant).find_by_name($evm.object['cloud_tenant']).id if $evm.object['cloud_tenant_id'].nil? && $evm.object['cloud_tenant']
  $evm.object['cloud_network_id'] = $evm.vmdb(:cloud_network).find_by_name($evm.object['cloud_network']).id if $evm.object['cloud_network_id'].nil? && $evm.object['cloud_network']

  log(:info, "Cloud Network ID: #{$evm.object['cloud_network_id'].inspect}")
  log(:info, "Cloud Network ID: #{$evm.object['cloud_network_id']} - Tenant ID: #{$evm.object['cloud_tenant_id']}")
  log(:info, "Cloud Network: #{$evm.object['cloud_network']} - Cloud Tenant: #{$evm.object['cloud_tenant']}")

  if $evm.object['fip_id']
    ips = $evm.vmdb(:floating_ip).where(["id = ?", $evm.object['fip_id']])
  else
    if $evm.object['fip'].nil?
      ips = $evm.vmdb(:floating_ip).all if $evm.object['cloud_tenant_id'].nil? && $evm.object['cloud_network_id'].nil?

      ips = $evm.vmdb(:floating_ip).where(["cloud_network_id = ?",  
                                      $evm.object['cloud_network_id']]) if $evm.object['cloud_tenant_id'].nil? &&
                                                                           !$evm.object['cloud_network_id'].nil? &&
                                                                           $evm.object['cloud_network_id']

      ips = $evm.vmdb(:floating_ip).where(["cloud_tenant_id = ?",  
                                      $evm.object['cloud_tenant_id']]) if $evm.object['cloud_tenant_id'] &&
                                                                          !$evm.object['cloud_tenant_id'].nil? &&
                                                                          $evm.object['cloud_network_id'].nil?

      ips = $evm.vmdb(:floating_ip).where(["cloud_network_id = ? and
                                      cloud_tenant_id = ?",
                                      $evm.object['cloud_network_id'],
                                      $evm.object['cloud_tenant_id']]) if $evm.object['cloud_tenant_id'] &&
                                                                          !$evm.object['cloud_tenant_id'].nil? &&
                                                                          $evm.object['cloud_network_id'] &&
                                                                          !$evm.object['cloud_network_id'].nil?
    else
      ips = $evm.vmdb(:floating_ip).where(["cloud_network_id = ? and
                                      cloud_tenant_id = ? and 
                                      address = ?",
                                      $evm.object['cloud_network_id'],
                                      $evm.object['cloud_tenant_id'],
                                      $evm.object['fip']]) if $evm.object['cloud_tenant_id'] && $evm.object['cloud_network_id'] &&
                                                              !$evm.object['cloud_tenant_id'].nil? && !$evm.object['cloud_network_id'].nil?

      ips = $evm.vmdb(:floating_ip).where(["cloud_network_id = ? and
                                      address = ?",
                                      $evm.object['cloud_network_id'],
                                      $evm.object['fip']]) if $evm.object['cloud_tenant_id'].nil? &&
                                                              $evm.object['cloud_network_id'] &&
                                                              !$evm.object['cloud_network_id'].nil?
      ips = $evm.vmdb(:floating_ip).where(["cloud_tenant_id = ? and
                                      address = ?",
                                      $evm.object['cloud_tenant_id'],
                                      $evm.object['fip']]) if $evm.object['cloud_tenant_id'] &&
                                                              !$evm.object['cloud_tenant_id'].nil? &&
                                                              $evm.object['cloud_network_id'].nil?
      ips = $evm.vmdb(:floating_ip).where(["address = ?", $evm.object['fip']]) if $evm.object['cloud_tenant_id'].nil? && $evm.object['cloud_network_id'].nil? 
    end
  end

  log(:info, "Floating IPS #{ips}")

  ip_list = {}
  ips.each { |f| ip_list[f.address] = { :id => f.id,
                                     :fixed_ip_address => f.fixed_ip_address,
                                     :network_provider => f.ext_management_system,
                                     :ext_floating_network => f.cloud_network_id.nil?? "" : $evm.vmdb(:cloud_network).find_by_id(f.cloud_network_id).name,
                                     :instance => f.vm_id.nil?? "" : $evm.vmdb(:vm).find_by_id(f.vm_id).name
                                   }} if ips

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

