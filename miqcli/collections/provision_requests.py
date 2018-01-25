# Copyright (C) 2017 Red Hat, Inc.
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

import click
import ast
from miqcli.decorators import client_api
from miqcli.constants import SUPPORTED_PROVIDERS, REQUIRED_OS_KEYS, \
    OPTIONAL_OS_KEYS, OPENSTACK_PAYLOAD
from miqcli.utils import log
import json


class Collections(object):
    """Provision requests collections."""

    @client_api
    def approve(self):
        """Approve."""
        raise NotImplementedError

    @click.option('--provider', type=str,
                  help='set a supported provider',
                  required=True)
    @click.option('--payload', type=str,
                  help='payload data for a provisioning request')
    @click.option('--payload_file', type=str,
                  help='file name of a json file of the data to' \
                       ' provision a resource')
    @client_api
    def create(self, provider, payload, payload_file):
        """Create."""
        # verify a valid provider
        if provider not in SUPPORTED_PROVIDERS:
            log.abort("Unsupported Provider, please select one from the " \
                      "supported list: {0}".format(SUPPORTED_PROVIDERS))
        if provider == "OpenStack":
            log.info("Attempt to create a provision request")
            input_data = ""
            # get our data
            if payload:
                input_data = ast.literal_eval(payload)
            elif payload_file:
                with open(payload_file) as f:
                    input_data = json.load(f)
            else:
                log.abort("Please set the payload or payload_file parameter")

            # verify all the required keys are set
            for key in REQUIRED_OS_KEYS:
                 if key not in input_data:
                     log.abort("{0} is a required key, please set it in the payload".format(key))

            # verify there are no invalid keys
            set_keys = list(input_data.keys())
            all_keys = OPTIONAL_OS_KEYS + REQUIRED_OS_KEYS
            invalid_keys = list(set(set_keys) - set(all_keys))
            if invalid_keys:
                log.abort("{0} is not a valid key for the OpenStack provider".format(invalid_keys))

            # Verified data is valid, update payload w/id lookups

            #set the email_address
            OPENSTACK_PAYLOAD["requester"]["owner_email"] = input_data["email"]
            OPENSTACK_PAYLOAD["vm_fields"]["vm_name"] = input_data["vm_name"]

            # lookup flavor
            flavor_list = self.api.basic_query(self.api.get_collection("flavors"),
                                               ("name", "=", input_data["flavor"]))
            if len(flavor_list) == 1:
                OPENSTACK_PAYLOAD["vm_fields"]["instance_type"] = flavor_list[0].id
            else:
                log.abort("Querying for passed flavor: {0} failed".format(input_data["flavor"]))

            # lookup image
            template_list = self.api.basic_query(self.api.get_collection("templates"),
                                                 ("name", "=", input_data["image"]))
            # getting multiple matches for some reason???
            if len(template_list) > 0:
                OPENSTACK_PAYLOAD["template_fields"]["guid"] = template_list[0].guid
            else:
                log.abort("Querying for passed image: {0} failed: {1}".format(
                    input_data["image"], template_list))

            # lookup security groups
            secgroup_list = self.api.basic_query(self.api.get_collection("security_groups"),
                                                 ("name", "=", input_data["security_group"]))
            if len(secgroup_list) == 1:
                OPENSTACK_PAYLOAD["vm_fields"]["security_groups"] = secgroup_list[0].id
            else:
                log.abort("Querying for passed security group: {0} failed".format(input_data["security_group"]))

            # lookup keypairs
            keypair_list = self.api.basic_query(self.api.get_collection("authentications"),
                                                ("name", "=", input_data["key_pair"]))
            if len(keypair_list) == 1:
                OPENSTACK_PAYLOAD["vm_fields"]["guest_access_key_pair"] = keypair_list[0].id
            else:
                log.abort("Querying for passed keypair: {0} failed".format(input_data["key_pair"]))

            # lookup cloud network
            cloudnetwork_list = self.api.basic_query(self.api.get_collection("cloud_networks"),
                                                     ("name", "=", input_data["network"]))
            if len(cloudnetwork_list) == 1:
                OPENSTACK_PAYLOAD["vm_fields"]["cloud_network"] = cloudnetwork_list[0].id
            else:
                log.abort("Querying for passed network: {0} failed".format(input_data["network"]))

            # lookup cloud tenant
            cloudtenant_list = self.api.basic_query(self.api.get_collection("cloud_tenants"),
                                                    ("name", "=", input_data["tenant"]))
            if len(cloudtenant_list) == 1:
                OPENSTACK_PAYLOAD["vm_fields"]["cloud_tenant"] = cloudtenant_list[0].id
            else:
                log.abort("Querying for passed network: {0} failed".format(input_data["tenant"]))

            # TODO: Add optional params to the payload (floating ip)

            log.debug("Payload for the provisioning request: {0}".format(OPENSTACK_PAYLOAD))

            outcome = self.action(OPENSTACK_PAYLOAD)
            provreq_id = outcome[0].id
            log.info("Provisioning request created: {0}".format(provreq_id))
            return_tuple = self.api.check_provision_request(provreq_id,
                                                            "provisioning vm: {}".format(input_data["vm_name"]))
            if return_tuple[0] == 0:
                log.info(return_tuple[1])
            else:
                log.abort(return_tuple[1])
        else:
            log.abort("Unsupported provider: {0}".format(provider))

    @client_api
    def deny(self):
        """Deny."""
        raise NotImplementedError

    @client_api
    def query(self):
        """Query."""
        raise NotImplementedError
