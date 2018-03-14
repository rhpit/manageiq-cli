# Copyright (C) 2018 Red Hat, Inc.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import json
from miqcli import Client
from time import sleep

# create a client object
# use the default credentials
client = Client()

# 1. Gather the input payload data
# Uncomment desired example
# Auto Placement or Specifying Placement (Network and Subnet)

# Auto Placement Example Payload File
# payload_file = "aws_provision_ex_auto_placement.json"

# Not Auto Placement - Specify Placement and cloud_subnet
payload_file = "aws_provision_ex_cloud_subnet.json"

with open(payload_file) as f:
    try:
        payload_data = json.load(f)
    except ValueError as e:
        print("Error loading json data: {0}".format(e))
        raise SystemExit(1)

# 2. call the provision request to create this vm (cli call to
#  provision_request create --provider Amazon this will return an id
client.collection = "provision_requests"
req_id = client.collection.create('Amazon', str(payload_data), "")
print("ID of the request: {0}".format(req_id))

# Query the provision request until it is active, then query
# the spawned request task
done = False
while not done:
    result = client.collection.status(req_id)
    if result.request_state == 'active' or result.request_state == 'finished':
        done = True
    sleep(5)

# 3. the script will query the request task until the state is finished
#  once finished, it will return information about the provisioned machine
#  or display the error message
client.collection = "request_tasks"
done = False
while not done:
    result = client.collection.status(req_id)
    if result.state == "finished":
        done = True
    sleep(5)

# 4. Report the floating ip address back to the user if there are no errors
if result.status == "Error":
    req_state = result.state
    req_status = result.status
    print("State: {0} and Status: {1}".format(req_state, req_status))
    print("Message: {0}".format(result.message))
else:
    # Get the data back from the provision_request
    client.collection = "provision_requests"
    result = client.collection.status(req_id)
    vm_name = payload_data["vm_name"]

    # Set key attributes if provided
    vm_provider = None
    vm_network = None
    vm_tenant = None
    vm_subnet = None
    if "provider" in payload_data and payload_data["provider"]:
        vm_provider = payload_data["provider"]
    if "network" in payload_data and payload_data["network"]:
        vm_network = payload_data["network"]
    if "subnet" in payload_data and payload_data["subnet"]:
        vm_subnet = payload_data["subnet"]
    if "tenant" in payload_data and payload_data["tenant"]:
        vm_tenant = payload_data["tenant"]

    try:
        client.collection = "instances"
        instances = client.collection.query(inst_name=vm_name,
                                            provider=vm_provider,
                                            network=vm_network,
                                            tenant=vm_tenant,
                                            subnet=vm_subnet,
                                            attr=("floating_ip",))
        if instances and type(instances) is list:
            print("Multiple instances found.")
            print("Unable to specify specific floating ip for created vm")
            raise SystemExit(1)
        elif not instances:
            print("Issues creating vm. No vm found to obtain floating ip")
            raise SystemExit(1)
        else:
            try:
                fip_id = instances["floating_ip"]["address"]
                print("Floating ip for {0}: {1}".format(vm_name, fip_id))
            except AttributeError as e:
                print('No associated floating ips for vm: {0}'.format(
                    instances["name"]))
    except SystemExit as e:
        print(e.message)
        raise SystemExit(1)
