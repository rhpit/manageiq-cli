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


from miqcli.constants import FLOATINGIP_PAYLOAD, SUPPORTED_AUTOMATE_TYPES, \
    OS_NETWORK_TYPE, OS_TYPE

from miqcli.utils import log, get_input_data

from miqcli.decorators import client_api


class Collections(object):
    """Automation requests collections."""

    @click.option('--type', type=str,
                  help='type of automation request',
                  required=True)
    @click.option('--payload', type=str,
                  help='payload data for an automation request')
    @click.option('--payload_file', type=str,
                  help='file name of the payload data for an '
                       'automation request')
    @client_api
    def create(self, type, payload, payload_file):
        """
        Create an automation request

        :param type: type of automation request
        :param payload: dictionary in string format
        :param payload_file: file location of the payload
        :return: id of the automation request
        """
        log.info("Attempt to create an automation request")

        # Verify the request is a supported request
        if type not in SUPPORTED_AUTOMATE_TYPES:
            log.abort("Invalid request, automate only supports options: "
                      "{0}".format(SUPPORTED_AUTOMATE_TYPES))

        # get the data from user input
        input_data = get_input_data(payload, payload_file)

        if type == "gen_floating_ip":
            # set the floating ip if set by the user
            if "fip_pool" in input_data and input_data["fip_pool"]:

                # lookup the cloud network
                pub_cloudnetwork_id_list = self.api.adv_query_getattr(
                    self.api.get_collection("cloud_networks"),
                    [("name", "=", input_data["fip_pool"]), "&",
                     ("type", "=", OS_NETWORK_TYPE + "::CloudNetwork::Public")
                     ], "id")
                # lookup cloud tenant
                cloudtenant_id_list = self.api.adv_query_getattr(
                    self.api.get_collection("cloud_tenants"),
                    [("name", "=", input_data["tenant"]), "&",
                     ("type", "=", OS_TYPE + "::CloudTenant")],
                    "id")

                if len(cloudtenant_id_list) == 1:
                    FLOATINGIP_PAYLOAD["parameters"]["cloud_tenant_id"] = \
                        cloudtenant_id_list[0]
                else:
                    log.abort("Querying for passed network: {0} failed".format(
                        input_data["tenant"]))

                FLOATINGIP_PAYLOAD["parameters"]["cloud_network_id"] = \
                    pub_cloudnetwork_id_list[0]

                outcome = self.action(FLOATINGIP_PAYLOAD)
                autoreq_id = outcome[0].id
                log.info("Automation request to generate a floating ip "
                         "created: {0}".format(autoreq_id))
                return(autoreq_id)

    @client_api
    def approve(self):
        """Approve."""
        raise NotImplementedError

    @client_api
    def deny(self):
        """Deny."""
        raise NotImplementedError

    @click.option('--id', type=str,
                  help='id of a specific automation request')
    @client_api
    def status(self, id):
        """
        Get the status of automation requests.
        :param id: id of the specific automation request
        :return: shows status and returns the automation_request obj.
        """

        status = OrderedDict()
        if id:
            automate_req_list = self.api.basic_query(self.collection,
                                                     ("id", "=", id))
            if len(automate_req_list) == 1:
                req = automate_req_list[0]
                status["state"] = req.request_state
                status["status"] = req.status
                status["message"] = req.message
                click.echo("STATUS of automation request {0}".format(id))
                for key in status:
                    click.echo("{0}: {1}".format(key, status[key]))
                return req
            else:
                log.abort("Unable to find an automation request with id: "
                          "{0}".format(id))
                return None
        else:
            click.echo("STATUS of all active automation requests:")
            automation_req_list = self.api.basic_query(
                self.collection,
                ("request_state", "!=", "finished"))

            if automation_req_list:
                for auto_req in automation_req_list:
                    click.echo("ID: {0}\tInstance: {1}\tSTATE: {2}\t STATUS:"
                               "{3}".format(auto_req.id,
                                            auto_req.options,
                                            auto_req.request_state,
                                            auto_req.status))
            else:
                click.echo("No active provisioning requests")
            return(automation_req_list)
