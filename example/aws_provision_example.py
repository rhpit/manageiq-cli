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

import json
from time import sleep

# create a client object
# pass in credentials, empty {} means it will use the default credentials
client = Client({})
print(client)

# 1. process json input
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

# 2. call the provision request to create this vm (cli call to
#  provision_request create --provider AWS this will return an id
client.collection = 'provision_requests'
req_id = client.collection.create('Amazon', str(payload_data), "")
print("ID of the provision request: {0}".format(req_id))

# 3. the script will keep querying the provision_request task for the status
#  to be finished, once finished, it will return information about the
#  provisioned machine or display the error message
done = False
while(not done):
    result = client.collection.status(req_id)
    if result.request_state == "finished":
        done = True
    sleep(5)

req_state = result.request_state
req_status = result.status
print("State: {0} and Status: {1}".format(req_state, req_status))
