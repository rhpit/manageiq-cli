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
from time import sleep

# The input to aws deletion is the name of the vm and provider name
# INPUT_VM_NAME = "<vm_name_to_delete>"
# INPUT_PROVIDER_NAME = "<name_of_provider>"
# INPUT_NETWORK = "<name_of_cloud_network>"
# INPUT_SUBNET = "<name_of_cloud_subnet>"

# Required Input Parameters
INPUT_VM_NAME = None
INPUT_PROVIDER_NAME = None

# Optional Input Parameter
INPUT_NETWORK = None
INPUT_SUBNET = None

client = Client()

# 1. Query the instance to obtain ID
client.collection = "instances"

try:
    instances = client.collection.query(inst_name=INPUT_VM_NAME,
                                        provider=INPUT_PROVIDER_NAME,
                                        network=INPUT_NETWORK,
                                        subnet=INPUT_SUBNET)
    if instances and type(instances) is list:
        print("Multiple instances found.")
        print("Supply more options to narrow selection")
        raise SystemExit(1)
    elif not instances:
        print("No Instance found to delete")
        raise SystemExit(1)
except SystemExit as e:
    print(e.message)
    raise SystemExit(1)

# 2. attempt to delete the instance
client.collection = "instances"
id = instances['id']
task_id = client.collection.terminate(inst_name=id,
                                      by_id=True)
print("INFO: Task ID of terminate instance: {0}".format(task_id))

# check the deletion task, and wait for it to be finished
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

# 3. remove the vm reference in MIQ/Cloudforms, if deletion is successful
client.collection = "vms"
task_id = client.collection.delete(vm_name=id,
                                   by_id=True)
print("INFO: Task ID for attempt to delete vm: {0}".format(task_id))

# check the task and make sure the vm reference is removed successfully
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
