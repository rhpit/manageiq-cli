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
import ast
from miqcli import Client
from time import sleep

# The input to deletion is the name of the vm and provider name
# INPUT_VM_NAME = "<vm_name_to_delete>"
# INPUT_PROVIDER_NAME = "<name_of_provider>"
# INPUT_NETWORK = "<name_of_cloud_network>"
# INPUT_TENANT = "<name_of_cloud_tenant>"
# INPUT_SUBNET = "<name_of_cloud_subnet>"

INPUT_VM_NAME = None
INPUT_PROVIDER_NAME = None
INPUT_NETWORK = None
INPUT_TENANT = None
INPUT_SUBNET = None


# create a client object
# pass in config, if empty {} means it will use the default credentials
config = {
    'username': 'admin',
    'password': 'smartvm',
    'url': 'https://localhost:8443',
    'enable_ssl_verify': False
}

client = Client(config)
fip_id = None

# 1. Query the instance to delete to see if the instance has a floating ip
# set the id of the floating ip as fip_id
client.collection = "instances"

try:
    instances = client.collection.query(inst_name=INPUT_VM_NAME,
                                        provider=INPUT_PROVIDER_NAME,
                                        network=INPUT_NETWORK,
                                        tenant=INPUT_TENANT,
                                        subnet=INPUT_SUBNET,
                                        attr=("floating_ip",
                                              "ext_management_system"))
    if instances and type(instances) is list:
        print("Multiple instances found.")
        print("Supply more options to narrow")
        raise SystemExit(1)
    elif not instances:
        print("No Instance found to delete")
        raise SystemExit(1)
    else:
        try:
            fip_id = instances["floating_ip"]["id"]
        except AttributeError as e:
            print('No associated floating ips for instance: {0}, will continue'
                  ' to delete.'.format(instances["name"]))
except SystemExit as e:
    print(e.message)
    raise SystemExit(1)

# 2. If there is a floating ip and this is an openstack instance,
# detach it and remove it
if fip_id and instances["vendor"] == "openstack":
    payload_data = {'floating_ip_id': fip_id}
    # detach the floating ip
    client.collection = "automation_requests"
    req_id = client.collection.create(
        method='release_floating_ip',
        payload=str(payload_data),
        payload_file=None)
    print(req_id)

    # 3. the script will keep querying automate_request for the status to be
    #  active, once active, it will query the spawned request task.
    done = False
    while not done:
        result = client.collection.status(req_id)
        if result.request_state == "active" or\
                result.request_state == "finished":
            done = True
        sleep(5)

    # Query the request task
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
    # detached and deleted.
    if "return" in result.options:
        return_data = result.options["return"]
        # verify the detaching was successful
        return_dict = ast.literal_eval(return_data)
        if return_dict["status"] != 202:
            print("Error deleting floating ip: %s" % return_dict)
            raise SystemExit(1)
    else:
        # unexpected error, maybe Automate Datastore not imported?
        print("Unexpected Error when deleting floating ip")
        raise SystemExit(1)

# 4. attempt to delete the instance
client.collection = "instances"
id = instances['id']
task_id = client.collection.terminate(inst_name=id,
                                      by_id=True)
print("Task ID of the deleted instance: {0}".format(task_id))

# 5. check the deletion task, and wait for it to be finished
client.collection = "tasks"
done = False
while not done:
    result = client.collection.status(task_id)
    if result.state == "Finished":
        done = True
    sleep(5)

if result.status == "Error":
    print("Deleting the instance: {0} failed: {1}".format(INPUT_VM_NAME,
                                                          result.message))
    raise SystemExit(1)

# 6. remove the vm reference in MIQ/Cloudforms, if deletion is successful
client.collection = "vms"
task_id = client.collection.delete(vm_name=id,
                                   by_id=True)
print("Task ID for the attempt to delete vm: {0}".format(task_id))

# 7. check the task and make sure the vm reference is removed successfully
client.collection = "tasks"
done = False
while not done:
    result = client.collection.status(task_id)
    if result.state == "Finished":
        done = True
    sleep(5)

if result.status == "Error":
    print("Deleting the VM reference: {0} failed: "
          "{1}".format(INPUT_VM_NAME, result.message))
    raise SystemExit(1)

print("Deletion successfully completed")
