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
from collections import OrderedDict

from miqcli.constants import SUPPORTED_PROVIDERS, REQUIRED_OSP_KEYS, \
    OSP_PAYLOAD, OSP_TYPE, OSP_NETWORK_TYPE
from miqcli.decorators import client_api
from miqcli.utils import log, get_input_data


class Collections(object):
    """Provision requests collections."""

    @client_api
    def approve(self):
        """Approve."""
        raise NotImplementedError

    @click.option('--provider', type=click.Choice(SUPPORTED_PROVIDERS),
                  help='provider to fulfill the provision request into.')
    @click.option('--payload', type=str,
                  help='provision request payload data.')
    @click.option('--payload_file', type=str,
                  help='filename containing JSON formatted payload data for '
                       'provision request.')
    @client_api
    def create(self, provider, payload, payload_file):
        """Create a provision request.

        ::
        Builds the payload data for the request (performing all necessary id
        lookups) and then submits the provision request to the server.

        :param provider: cloud provider to fulfill provision request into
        :type provider: str
        :param payload: json data in str format
        :type payload: str
        :param payload_file: file location of the payload
        :type payload_file: str
        :return: provision request ID
        :rtype: str
        """
        if provider == "OpenStack":
            log.info("Attempt to create a provision request")

            # get the data from user input
            input_data = get_input_data(payload, payload_file)

            # verify all the required keys are set
            missing_data = []
            for key in REQUIRED_OSP_KEYS:
                if key not in input_data or input_data[key] is None:
                    missing_data.append(key)
            if missing_data:
                log.abort("Required key(s) missing: {0}, please set it in "
                          "the payload".format(missing_data))

            # Verified data is valid, update payload w/id lookups
            # set the email_address and vm name
            OSP_PAYLOAD["requester"]["owner_email"] = input_data["email"]
            OSP_PAYLOAD["vm_fields"]["vm_name"] = input_data["vm_name"]

            if "floating_ip_id" in input_data and input_data["floating_ip_id"]:
                OSP_PAYLOAD["vm_fields"]["floating_ip_address"] = \
                    input_data["floating_ip_id"]

            # lookup flavor
            flavor_id_list = self.api.adv_query_getattr(
                self.api.get_collection("flavors"),
                [("name", "=", input_data["flavor"]),
                 "&", ("type", "=", OSP_TYPE + "::Flavor")],
                "id")
            if len(flavor_id_list) == 1:
                OSP_PAYLOAD["vm_fields"]["instance_type"] = \
                    flavor_id_list[0]
            else:
                log.abort("Querying for passed flavor: {0} failed".format(
                    input_data["flavor"]))

            # lookup image
            template_id_list = self.api.adv_query_getattr(
                self.api.get_collection("templates"),
                [("name", "=", input_data["image"]), "&",
                 ("type", "=", OSP_TYPE + "::Template")],
                "guid")

            # getting multiple matches for some reason???, just taking first
            # TODO investigate and fix
            if len(template_id_list) > 0:
                OSP_PAYLOAD["template_fields"]["guid"] = template_id_list[0]
            else:
                log.abort("Querying for passed image: {0} failed".format(
                    input_data["image"]))

            # lookup  security group
            secgroup_id_list = self.api.adv_query_getattr(
                self.api.get_collection("security_groups"),
                [("name", "=", input_data["security_group"]), "&",
                 ("type", "=", OSP_NETWORK_TYPE + "::SecurityGroup")],
                "id")
            if len(secgroup_id_list) == 1:
                OSP_PAYLOAD["vm_fields"]["security_groups"] = \
                    secgroup_id_list[0]
            else:
                log.abort("Querying for passed security group: {0} "
                          "failed".format(input_data["security_group"]))

            # lookup keypair
            keypair_id_list = self.api.adv_query_getattr(
                self.api.get_collection("authentications"),
                [("name", "=", input_data["key_pair"]), "&",
                 ("type", "=", OSP_TYPE + "::AuthKeyPair")],
                "id")
            if len(keypair_id_list) == 1:
                OSP_PAYLOAD["vm_fields"]["guest_access_key_pair"] = \
                    keypair_id_list[0]
            else:
                log.abort("Querying for passed keypair: {0} "
                          "failed".format(input_data["key_pair"]))

            # lookup cloud network
            cloudnetwork_id_list = self.api.adv_query_getattr(
                self.api.get_collection("cloud_networks"),
                [("name", "=", input_data["network"]), "&",
                 ("type", "=", OSP_NETWORK_TYPE + "::CloudNetwork::Private")],
                "id")
            if len(cloudnetwork_id_list) == 1:
                OSP_PAYLOAD["vm_fields"]["cloud_network"] = \
                    cloudnetwork_id_list[0]
            else:
                log.abort("Querying for passed network: {0} "
                          "failed".format(input_data["network"]))

            # lookup cloud tenant
            cloudtenant_id_list = self.api.adv_query_getattr(
                self.api.get_collection("cloud_tenants"),
                [("name", "=", input_data["tenant"]), "&",
                 ("type", "=", OSP_TYPE + "::CloudTenant")],
                "id")

            if len(cloudtenant_id_list) == 1:
                OSP_PAYLOAD["vm_fields"]["cloud_tenant"] = \
                    cloudtenant_id_list[0]
            else:
                log.abort("Querying for passed network: {0} failed".format(
                    input_data["tenant"]))

            log.debug("Payload for the provisioning request: {0}".format(
                OSP_PAYLOAD))
            outcome = self.action(OSP_PAYLOAD)
            provreq_id = outcome[0].id
            log.info("Provisioning request created: {0}".format(provreq_id))
            return(provreq_id)
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

    @click.option('--id', type=str,
                  help='id of a specific provisioning request')
    @client_api
    def status(self, id):
        """Print the status for a provision request.

        ::
        Handles getting information for an existing provision request and
        displaying/returning back to the user.

        :param id: id of the provisioning request
        :return: display output of the status and return a provisioning
                 request object.
        """

        status = OrderedDict()
        if id:
            provision_req_list = self.api.basic_query(self.collection,
                                                      ("id", "=", id))
            if len(provision_req_list) == 1:
                req = provision_req_list[0]
                status["state"] = req.request_state
                status["status"] = req.status
                status["message"] = req.message
                click.echo("STATUS of provision request {0} ({1})".format(
                    id, req.options["vm_name"]))
                for key in status:
                    click.echo("{0}: {1}".format(key, status[key]))
                return req
            else:
                log.abort("Unable to find a provision request with id: "
                          "{0}".format(id))
                return None
        else:
            click.echo("STATUS of all active provisioning requests:")
            provision_req_list = self.api.basic_query(
                self.collection,
                ("request_state", "!=", "finished"))

            if provision_req_list:
                for prov_req in provision_req_list:
                    click.echo("ID: {0}\tInstance: {1}\tSTATE: {2}\t STATUS:"
                               " {3}".format(prov_req.id,
                                             prov_req.options["vm_name"],
                                             prov_req.request_state,
                                             prov_req.status))
            else:
                click.echo("No active provisioning requests")
            return(provision_req_list)
