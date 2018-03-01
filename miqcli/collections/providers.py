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
from collections import Mapping
from manageiq_client.api import APIException

from miqcli.collections import CollectionsMixin
from miqcli.constants import SUPPORTED_PROVIDERS
from miqcli.decorators import client_api
from miqcli.provider import Provider
from miqcli.query import BasicQuery
from miqcli.utils import log


class ProviderTypes(Mapping):
    """Provider types.

    Class used for mapping ManageIQ provider class names. These are static
    names and at this time we are unable to retrieve these by REST API
    providers collection. Providers collection only shows providers and their
    type when added.
    """

    def __init__(self):
        """Constructor.

        The bulk of the work is here, this is where we will define the
        matrix mapping provider name to its ManageIQ provider class.
        """
        self.__dict__.update(
            amazon='ManageIQ::Providers::Amazon::CloudManager',
            openstack='ManageIQ::Providers::Openstack::CloudManager'
        )

    def __getitem__(self, item):
        """Get the provided keys value.

        :param item: key name
        :return: key value
        """
        return self.__dict__[item.lower()]

    def __iter__(self):
        """Returns a new iterator object based on the provider matrix.

        :return: iterator object
        """
        return iter(self.__dict__)

    def __len__(self):
        """Returns the length of the provider matrix

        :return: total number of provider types in the matrix
        """
        return len(self.__dict__)


class Collections(CollectionsMixin):
    """Providers collections."""

    @client_api
    def query(self):
        """Query.

        ::
        Query  a provider in manageiq.
        """
        raise NotImplementedError

    @staticmethod
    def _provider_exist(name, api):
        """Determine whether the provider exists.

        :param name: provider name
        :param api: client api pointer
        """
        provider = Provider(name, api)
        if provider.cloud_type:
            log.debug('Provider: %s exists in manageiq.' % name)
            found = True
        else:
            log.debug('Provider: %s does not exist in manageiq.' % name)
            found = False
        return found

    @click.argument('name', type=click.Choice(SUPPORTED_PROVIDERS))
    @click.option('--hostname', type=str, help='provider hostname/IP address.')
    @click.option('--port', type=str, help='provider API port.')
    @click.option('--region', type=str, help='provider region.')
    @click.option('--zone', type=str, help='manageiq zone for the provider.')
    @click.option('--username', type=str, help='provider username.',
                  required=True)
    @click.option('--password', type=str, help='provider password.',
                  required=True)
    @client_api
    def create(self, name, hostname=None, port=None, region=None, zone=None,
               username=None, password=None):
        """Create.

        ::
        Create a new provider in manageiq.

        :param name: provider name
        :param hostname: provider server hostname
        :param port: provider port
        :param region: provider region
        :param zone: manageiq zone
        :param username: provider username
        :param password: provider password
        :return: request id
        """
        _api = getattr(self, 'api')

        if self._provider_exist(name, _api):
            log.abort('Unable to process request to create provider: %s. '
                      'The provider already exists.' % name)

        log.info('Create provider: %s.' % name)

        # okay good to go, lets create the payload
        _payload = dict(
            name=name,
            type=ProviderTypes().get(name),
            provider_region=region,
            hostname=hostname,
            port=port,
            zone=zone,
            credentials=[
                dict(
                    userid=username,
                    password=password
                )
            ]
        )

        # zone requires href destination over string type
        if zone:
            query = BasicQuery(getattr(_api.client.collections, 'zones'))
            query(('name', '=', zone))

            if query.resources:
                # RFE: remove using static position in list
                _payload.update(dict(zone=dict(
                    href=getattr(query.resources[0], '_href').replace(
                        'zones', 'zone'))))

        log.debug('Payload:\n %s' % pformat(_payload))

        try:
            self.req_id = getattr(self, 'action')(_payload)
            log.info('Successfully submitted request to create provider: %s.'
                     % name)
            log.info('Create provider request ID: %s.' % self.req_id)
            return self.req_id
        except APIException as ex:
            log.abort('Request to create provider: %s failed!\n Error: %s' %
                      (name, ex))

    @client_api
    def edit(self):
        """Edit.

        ::
        Edit an existing provider in manageiq.
        """
        raise NotImplementedError

    @click.argument('name', type=click.Choice(SUPPORTED_PROVIDERS))
    @client_api
    def refresh(self, name):
        """Refresh.

        ::
        Refresh an existing provider in manageiq.

        :param name: provider name
        :return: request id
        """
        _api = getattr(self, 'api')

        # quit if provider given does not exists in manageiq
        if not self._provider_exist(name, _api):
            log.abort('Unable to process request to refresh provider: %s. '
                      'The provider does not exist in manageiq.' % name)

        # get the provider id
        query = BasicQuery(getattr(_api.client.collections, 'providers'))
        query(('name', '=', name))

        # okay good to go, lets create the payload
        # RFE: multiple resources? this only gives first index in list
        _payload = dict(id=query.resources.pop()['id'])

        log.debug('Payload:\n %s' % pformat(_payload))

        try:
            self.req_id = getattr(self, 'action')(_payload)
            log.info('Successfully submitted request to refresh provider: %s.'
                     '\nRequest ID: %s.' % (name, self.req_id))
            return self.req_id
        except APIException as ex:
            log.abort('Request to refresh provider: %s failed!\n Error: %s' %
                      (name, ex))

    @click.argument('name', type=click.Choice(SUPPORTED_PROVIDERS))
    @client_api
    def delete(self, name):
        """Delete.

        ::
        Delete an existing provider in manageiq.

        :param name: provider name
        :return: request id
        """
        _api = getattr(self, 'api')

        if not self._provider_exist(name, _api):
            log.abort('Unable to process request to delete provider: %s. '
                      'The provider does not exist.' % name)

        # get the provider id
        query = BasicQuery(getattr(_api.client.collections, 'providers'))
        query(('name', '=', name))

        # okay good to go, lets create the payload
        _payload = dict(id=query.resources.pop()['id'])

        log.debug('Payload:\n %s' % pformat(_payload))

        try:
            self.req_id = getattr(self, 'action')(_payload)
            log.info('Successfully submitted request to delete provider: %s.\n'
                     'Request ID: %s.' % (name, self.req_id))
            return self.req_id
        except APIException as ex:
            log.abort('Request to delete provider: %s failed!\n Error: %s' %
                      (name, ex))
