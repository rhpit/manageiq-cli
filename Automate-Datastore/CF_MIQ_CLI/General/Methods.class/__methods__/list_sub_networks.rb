#
# Description: Obtain sub_networks for given network.
# Cloud network        (optional) - Network Either by name or ID
# cloud_network        (string)     vpc-56944a3e 
# cloud_network_id     (integer)    3
# Cloud Subnetwork     (optional) - Subnetwork Either by name or ID
# cloud_sub_network    (string)     2
# cloud_sub_network_id (integer)    subnet-9753f7ff
# Returned list of sub_networks, ids, CIDR and cloud_network
#
begin
  # Method logger
  def log(level, msg)
    @method = 'list_sub_networks'
    $evm.log(level, "#{@method}: #{msg}")
  end
 
  # Method error logger
  def log_err(err)
    log(:error, "#{err.class} #{err}")
    log(:error, "#{err.backtrace.join("\n")}")
  end

  log(:info, "List SubNets")

  # Validate Input Parameters
  # Process Cloud Network Input Parameter
  if $evm.object['cloud_network'] and $evm.object['cloud_network_id']
    raise ArgumentError,
          'To many arguments given - Specify Network by Name or ID not both'
  end

  # Process Cloud Sub Network Parameter
  if $evm.object['cloud_sub_network'] and $evm.object['cloud_sub_network_id']
    raise ArgumentError,
     'To many arguments given - Specify Cloud SubNetwork by Name or ID not both'
  end

  # Get SubNetwork by ID if given.
  if $evm.object['cloud_sub_network_id']
    sub_networks = $evm.vmdb(:cloud_subnet).where("id = ?",
                   $evm.object['cloud_sub_network_id'])
    if sub_networks.nil? || sub_networks.length == 0
      raise ArgumentError,
        "Cloud Subnet ID: #{$evm.object['cloud_sub_network_id']} not found"
    end
  end

  # Get Networks by Name if input
  if $evm.object['cloud_network']
    cloud_networks = $evm.vmdb(:cloud_network).where("name = ?",
                               $evm.object['cloud_network'])

    # If only one Network set cloud_network_id
    if cloud_networks && cloud_networks.length == 1
      $evm.object['cloud_network_id'] = cloud_networks[0].id
      $evm.object['cloud_network'] = nil
    elsif cloud_networks.nil? || cloud_networks.length == 0
      raise ArgumentError,
        "Cloud Network: #{$evm.object['cloud_network']} not found"
    end
  end

  log(:info, "Cloud Network ID: #{$evm.object['cloud_network_id']
              } - Cloud Sub Network ID: #{$evm.object['cloud_sub_network_id']}")
  log(:info, "Cloud Network: #{$evm.object['cloud_network']
              } - Cloud Sub Network: #{$evm.object['cloud_sub_network']}")

  # Get sub networks with correct command. Based on input arguments
  # cloud sub network not input as ID
  if $evm.object['cloud_sub_network_id'].nil?
    if $evm.object['cloud_sub_network']
      if $evm.object['cloud_network_id']
        # Input of Cloud Subnet and Cloud Network ID
        sub_networks = $evm.vmdb(:cloud_subnet).where(
                           "cloud_network_id = ? and name = ?",
                           $evm.object['cloud_network_id'],
                           $evm.object['cloud_sub_network'])
        if sub_networks.nil? || sub_networks.length == 0
          raise ArgumentError,
            "Cloud Subnet: #{$evm.object['cloud_sub_network']} not found for Cloud Network ID: #{$evm.object['cloud_network_id']}"
        end
      else
        # Input of Cloud Subnet
        sub_networks = $evm.vmdb(:cloud_subnet).where(
                           "name = ?", $evm.object['cloud_sub_network'])
        if sub_networks.nil? || sub_networks.length == 0  
          raise ArgumentError,
            "Cloud Subnet: #{$evm.object['cloud_sub_network']} not found"
        end
      end
    elsif $evm.object['cloud_network_id']                          
      # Input of Cloud Network ID
      sub_networks = $evm.vmdb(:cloud_subnet).where("cloud_network_id = ?",
                         $evm.object['cloud_network_id'])
      if sub_networks.nil? || sub_networks.length == 0
        raise ArgumentError,
          "No Cloud Subnets found for Cloud Network ID: #{$evm.object['cloud_network_id']}"
      end
    else
      # No Input given. Get all
      sub_networks = $evm.vmdb(:cloud_subnet).all 
      if sub_networks.nil? || sub_networks.length == 0
        raise ArgumentError, "No Cloud Subnets found"
      end
    end
  elsif $evm.object['cloud_network_id']
    # Input of Cloud Network ID and Cloud Sub Network ID - Validate Match
    if sub_networks[0].cloud_network_id != $evm.object['cloud_network_id'].to_i
        raise ArgumentError,
          "Cloud Subnet's Network: #{sub_networks[0].cloud_network_id} does not match Cloud Network ID: #{$evm.object['cloud_network_id']} supplied"
    end 
  end

  # Process Multiple Networks. Input was by Name. Only get subnetworks for networks in list
  sn = []
  if cloud_networks && cloud_networks.length > 1
    cloud_networks.each { |f| sub_networks.each { |g| sn << g if f.id == g.cloud_network_id }}
    sub_networks = sn
  end

  log(:info, "Cloud Sub Networks #{sub_networks}")

  # Format return data
  sn_list = {}
  sub_networks.each { |f| sn_list[f.name] = { :id => f.id,
                                     :cidr => f.cidr,
                                     :network_provider => $evm.vmdb(:cloud_network).find_by_id(f.cloud_network_id).ext_management_system
                                   }} if sub_networks

  # For automation_task set return data. status and return data
  # List of sub networks and their IDs
  case $evm.root['vmdb_object_type']
    when 'automation_task'
      automation_request = $evm.root['automation_task'].automation_request
      automation_request.set_option(:return, JSON.generate({:status => 'success',
                                                            :return => sn_list}))
  end
  exit MIQ_OK

# Handle Errors
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

