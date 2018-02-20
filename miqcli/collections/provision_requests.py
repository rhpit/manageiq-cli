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

from pprint import pformat

import click
from collections import OrderedDict

from miqcli.collections import CollectionsMixin
from miqcli.constants import SUPPORTED_PROVIDERS, REQUIRED_OSP_KEYS, \
    OSP_PAYLOAD, REQUIRED_AWS_AUTO_PLACEMENT_KEYS, AWS_PAYLOAD, \
    REQUIRED_AWS_PLACEMENT_KEYS
from miqcli.decorators import client_api
from miqcli.provider import Flavors, KeyPair, Networks, SecurityGroups,\
    Templates, Tenant
from miqcli.query import BasicQuery
from miqcli.utils import log, get_input_data


class Collections(CollectionsMixin):
    """Provision requests collections."""

    @client_api
    def approve(self):
        """Approve."""
        raise NotImplementedError

    @click.option('--provider', type=click.Choice(SUPPORTED_PROVIDERS),
                  required=True, help='provider to fulfill the provision '
                                      'request into.')
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
        # RFE: make generic as possible, remove conditional per provider
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

            if 'floating_ip_id' in input_data:
                OSP_PAYLOAD['vm_fields']['floating_ip_address'] = \
                    input_data['floating_ip_id']

            # lookup flavor resource to get the id
            flavors = Flavors(provider, self.api)
            OSP_PAYLOAD['vm_fields']['instance_type'] = flavors.get_id(
                input_data['flavor'])

            # lookup image resource to get the id
            templates = Templates(provider, self.api)
            OSP_PAYLOAD['template_fields']['guid'] = templates.get_id(
                input_data['image']
            )

            if 'security_group' in input_data and input_data['security_group']:
                # lookup security group resource to get the id
                sec_group = SecurityGroups(provider, self.api)
                OSP_PAYLOAD['vm_fields']['security_groups'] = sec_group.get_id(
                    input_data['security_group']
                )

            if 'key_pair' in input_data and input_data["key_pair"]:
                # lookup key pair resource to get the id
                key_pair = KeyPair(provider, self.api)
                OSP_PAYLOAD['vm_fields']['guest_access_key_pair'] = \
                    key_pair.get_id(input_data['key_pair'])

            # lookup cloud network resource to get the id
            network = Networks(provider, self.api, 'private')
            OSP_PAYLOAD['vm_fields']['cloud_network'] = network.get_id(
                input_data['network']
            )

            # lookup cloud tenant resource to get the id
            tenant = Tenant(provider, self.api)
            OSP_PAYLOAD['vm_fields']['cloud_tenant'] = tenant.get_id(
                input_data['tenant']
            )

            log.debug("Payload for the provisioning request: {0}".format(
                pformat(OSP_PAYLOAD)))
            self.req_id = self.action(OSP_PAYLOAD)
            log.info("Provisioning request created: {0}".format(self.req_id))
            return self.req_id

        # RFE: make generic as possible, remove conditional per provider
        if provider == "Amazon":
            log.info("Attempt to create a provision request")

            # get the data from user input
            input_data = get_input_data(payload, payload_file)

            # Set Required fields
            if 'auto_placement' in input_data and input_data['auto_placement']:
                REQUIRED_AWS_KEYS = REQUIRED_AWS_AUTO_PLACEMENT_KEYS
            else:
                REQUIRED_AWS_KEYS = REQUIRED_AWS_PLACEMENT_KEYS
            # verify all the required keys are set
            missing_data = []
            for key in REQUIRED_AWS_KEYS:
                if key not in input_data or input_data[key] is None:
                    missing_data.append(key)
            if missing_data:
                log.abort("Required key(s) missing: {0}, please set it in "
                          "the payload".format(missing_data))

            # Verified data is valid, update payload w/id lookups
            # set the email_address and vm name
            AWS_PAYLOAD["requester"]["owner_email"] = input_data["email"]
            AWS_PAYLOAD["vm_fields"]["vm_name"] = input_data["vm_name"]

            # lookup flavor resource to get the id
            flavors = Flavors(provider, self.api)
            AWS_PAYLOAD['vm_fields']['instance_type'] = flavors.get_id(
                input_data['flavor'])

            # lookup image resource to get the id
            templates = Templates(provider, self.api)
            AWS_PAYLOAD['template_fields']['guid'] = templates.get_id(
                input_data['image']
            )

            # lookup security group resource to get the id
            if 'security_group' in input_data and input_data['security_group']:
                sec_group = SecurityGroups(provider, self.api)
                AWS_PAYLOAD['vm_fields']['security_groups'] = \
                    sec_group.get_id(input_data['security_group'])

            # lookup key pair resource to get the id
            key_pair = KeyPair(provider, self.api)
            AWS_PAYLOAD['vm_fields']['guest_access_key_pair'] = \
                key_pair.get_id(input_data['key_pair'])

            # lookup cloud network resource to get the id
            if 'network' in input_data and input_data['network']:
                network = Networks(provider, self.api)
                AWS_PAYLOAD['vm_fields']['cloud_network'] = network.get_id(
                    input_data['network']
                )

            # lookup cloud_subnets attribute from cloud network entity
            # to get the id
            if 'subnet' in input_data and input_data['subnet']:
                out = network.get_attribute(
                    AWS_PAYLOAD['vm_fields']['cloud_network'],
                    'cloud_subnets')

                # Get id for supplied Subnet
                subnet_id = None
                if isinstance(out, list):
                    for att in out:
                        if 'name' in att and att['name'] == \
                                input_data['subnet']:
                            subnet_id = att['id']
                elif isinstance(out, dict):
                    if out and 'name' in out and out['name'] == \
                            input_data['subnet']:
                        subnet_id = out['id']

                if subnet_id is None:
                    log.abort('Cannot obtain Cloud Subnet: {0} info, please '
                              'check setting in the payload '
                              'is correct'.format(input_data['subnet']))

                log.info('Attribute: {0}'.format(out))
                AWS_PAYLOAD['vm_fields']['cloud_subnet'] = subnet_id

            log.debug("Payload for the provisioning request: {0}".format(
                pformat(AWS_PAYLOAD)))
            self.req_id = self.action(AWS_PAYLOAD)
            log.info("Provisioning request created: {0}".format(self.req_id))
            return self.req_id

    @client_api
    def deny(self):
        """Deny."""
        raise NotImplementedError

    @client_api
    def query(self):
        """Query."""
        raise NotImplementedError

    @click.argument('req_id', metavar='ID', type=str, default='')
    @client_api
    def status(self, req_id):
        """Print the status for a provision request.

        ::
        Handles getting information for an existing provision request and
        displaying/returning back to the user.

        :param req_id: id of the provisioning request
        :type req_id: str
        :return: provision request object or list of provision request objects
        """
        status = OrderedDict()
        query = BasicQuery(self.collection)

        if req_id:
            provision_requests = query(("id", "=", req_id))

            if len(provision_requests) < 1:
                log.warning('Provision request id: %s not found!' % req_id)
                return None

            req = provision_requests[0]
            status['state'] = req.request_state
            status['status'] = req.status
            status['message'] = req.message
            log.info('-' * 50)
            log.info('Provision request'.center(50))
            log.info('-' * 50)
            log.info(' * ID: %s' % req_id)
            log.info(' * VM: %s' % req.options['vm_name'])
            for key, value in status.items():
                log.info(' * %s: %s' % (key.upper(), value))
            log.info('-' * 50)

            return req
        else:
            provision_requests = query(("request_state", "!=", "finished"))

            if len(provision_requests) < 1:
                log.warning(' * No active provision requests at this time')
                return None

            log.info('-' * 50)
            log.info(' Active provision requests'.center(50))
            log.info('-' * 50)

            for item in provision_requests:
                log.info(' * ID: %s\tINSTANCE: %s\tSTATE: %s\tSTATUS: %s' %
                         (item.id, item.options['vm_name'], item.request_state,
                          item.status))
            log.info('-' * 50)

            return provision_requests
