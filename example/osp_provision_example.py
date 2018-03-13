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

from miqcli import Client
import ast
import json
from time import sleep

# create a client object
client = Client()

# 1. Gather the input payload data
payload_file = "openstack_provision_ex.json"

with open(payload_file) as f:
    try:
        payload_data = json.load(f)
    except ValueError as e:
        print("Error loading json data: {0}".format(e))
        raise SystemExit(1)

if "fip_pool" in payload_data and payload_data["fip_pool"]:
    # 2. the script will first make an automate request to get a floating ip
    # (cli call to automate get_floating_ip) this call returns an id to watch
    # if the "fip_pool" id is set, if not it will skip this step.
    client.collection = "automation_requests"
    req_id = client.collection.create(
        method='gen_floating_ip', payload=str(payload_data), payload_file=None)

    # 3. the script will keep querying automate_request for the status to be
    #  active, once active, it will monitor the spawned request task.
    done = False
    while not done:
        result = client.collection.status(req_id)
        if result.request_state == "active" or\
                result.request_state == "finished":
            done = True
        sleep(5)

    # 4. the script will keep querying request task and wait for the state to
    #  be finished, once finished, it will query for the floating ip id. If
    #  there was an error, the script will display the error message and exit.
    client.collection = "request_tasks"
    done = False
    while not done:
        result = client.collection.status(req_id)
        if result.state == "finished":
            done = True
        sleep(5)

    # Task is complete, go back to the automation request to get the output
    client.collection = "automation_requests"
    result = client.collection.status(req_id)

    # see the return and options of the automate request
    print("Options from the automate request: {0}".format(result.options))

    # verify from the automate output that a floating ip was successfully
    # created, and extract the id of the floating ip address
    if "return" in result.options:
        return_data = result.options["return"]
    else:
        # unexpected error, maybe Automate Datastore not imported?
        print("Unexpected Error when getting floating ip")
        raise SystemExit(1)
    return_dict = ast.literal_eval(return_data)
    if return_dict["status"] == "success":
        fip = next(iter(return_dict['return']))
        fip_id = return_dict['return'][fip]
        print("got floating ip: {0}: {1}".format(fip, fip_id))
    else:
        print("error occurred: {0}".format(
            return_dict["return"]))
        raise SystemExit(1)

    # 4. the script will update the json data (in memory) w/ the floating_ip_id
    payload_data["floating_ip_id"] = fip_id
    print("updated payload data w/floating ip: {0}".format(payload_data))

# 5. call the provision request to create this vm (cli call to
#  provision_request create --provider OpenStack this will return an id
client.collection = 'provision_requests'
req_id = client.collection.create('OpenStack', str(payload_data), "")
print("ID of the request: {0}".format(req_id))

# Query the provision request until it is active, then query
# the spawned request task
done = False
while not done:
    result = client.collection.status(req_id)
    if result.request_state == "active" or result.request_state == "finished":
        done = True
    sleep(5)

# 6. the script will query the request task until the state is finished,
#  once finished, it will return information about the provisioned machine
#  or display the error message
client.collection = "request_tasks"
done = False
while not done:
    result = client.collection.status(req_id)
    if result.state == "finished":
        done = True
    sleep(5)

# 7. Report the floating ip address back to the user if there are no errors
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
    if "provider" in payload_data and payload_data["provider"]:
        vm_provider = payload_data["provider"]
    if "network" in payload_data and payload_data["network"]:
        vm_network = payload_data["network"]
    if "tenant" in payload_data and payload_data["tenant"]:
        vm_tenant = payload_data["tenant"]

    try:
        client.collection = "instances"
        instances = client.collection.query(inst_name=vm_name,
                                            provider=vm_provider,
                                            network=vm_network,
                                            tenant=vm_tenant,
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
