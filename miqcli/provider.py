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

from manageiq_client.api import APIException
from manageiq_client.filters import Q

from miqcli.utils import log

__all__ = ['Flavors', 'Templates', 'SecurityGroups', 'KeyPair', 'Tenant',
           'Networks']


class Provider(object):
    """Cloud provider parent class.

    Cloud provider component 'child' classes all inherit this class. It
    provides provider component classes with data they need..
    """

    __collection_name__ = ''

    # declare attributes to be defined at a later time..
    _type, _cloud_type, _network_type = '', '', ''
    _collection = None

    def __init__(self, name, api):
        """Constructor.

        :param name: provider name
        :type name: str
        :param api: client api pointer
        :type api: class
        """
        self._name = name
        self._api = api

        # lets first save the provider types for cloud & network
        for res in self._api.client.collections.providers.all:
            if self._name.lower().title() in res.type:
                if 'cloud' in res.type.lower():
                    self._cloud_type = res.type
                elif 'network' in res.type.lower():
                    self._network_type = res.type

    @property
    def name(self):
        """Provider name property.

        :return: provider name
        :rtype: str
        """
        return self._name

    @property
    def api(self):
        """Client API pointer property.

        :return: client api pointer
        :rtype: class
        """
        return self._api

    @property
    def type(self):
        """Resource type property.

        :return: resource type
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, value):
        """Set the resource type.

        :param value: resource name
        :type value: str
        """
        self._type = value

    @property
    def cloud_type(self):
        """Cloud type property.

        :return: resource cloud type
        :rtype: str
        """
        return self._cloud_type

    @property
    def network_type(self):
        """Network type property.

        :return: resource network type
        :rtype: str
        """
        return self._network_type

    @property
    def collection(self):
        """Runtime collection property.

        This property contains the collection that is being used.

        :return: collection
        :rtype: class
        """
        return self._collection

    @collection.setter
    def collection(self, value):
        """Set the collection object.

        :param value: collection name
        :type value: str
        """
        self._collection = getattr(self.api.client.collections, value)

    def get_entity(self, id, attributes):
        """Get the element based on the id given.
        :param id: resource id
        :type id: int
        :param attributes: List of attributes
        :type attributes: Comma seperated string
        :return: element or none
        :rtype: dict
        """
        try:
            output = self.collection.__call__(id, attributes)
        except (APIException, ValueError):
            log.debug("Error getting element {0} for """
                      "{1}".format(id, self.__collection_name__))

        return output

    def get_resource(self, name):
        """Get the resource based on the name given.
        :param name: resource name
        :type name: str
        :return: resource or none
        :rtype: dict or None
        """
        output = None
        query = Q('name', '=', name) & Q('type', '=', self.type)

        try:
            output = self.collection.filter(query)
        except (APIException, ValueError):
            log.debug("Invalid query attempted {0} for """
                      "{1}".format(query, self.__collection_name__))

        if len(output.resources) == 1:
            resource = output.resources[0]
        elif len(output.resources) > 1:
            log.warning('Multiple resources match %s:%s.' % (
                self.__collection_name__, name))
            # RFE: handle multiple resources with same name/provider
            # this should be very unlikely that we get multiples, for now we
            # will return first match
            resource = output.resources[0]
        else:
            resource = None
        return resource

    def get_id(self, name):
        """Get the ID for the resource name.

        :param name: resource name
        :type name: str
        :return: resource id
        :rtype: int
        """
        return self.get_resource(name)['id']

    def get_attribute(self, ent_id, attribute):
        """Get the attribute for the collection entity.

        :param ent_id: Entity ID of Collection
        :type ent_id: id
        :param attribute: Attribute to retrieve
        :type attribute: string
        :return: Attribute
        :rtype:
        """
        atts = self.get_entity(ent_id ,attribute).__getattr__(attribute)
        return atts

class Flavors(Provider):
    """Provider flavor component."""

    __collection_name__ = 'flavors'

    def __init__(self, name, api):
        """Constructor."""
        super(Flavors, self).__init__(name, api)
        self.collection = self.__collection_name__
        self.type = self.cloud_type + '::Flavor'

    def get_resource(self, name):
        """Override the parent get_resource."""
        val = super(Flavors, self).get_resource(name)
        if val is None:
            log.abort('Flavor %s not found for provider %s.' %
                      (name, self.name))
        return val


class Templates(Provider):
    """Provider images component."""

    __collection_name__ = 'templates'

    def __init__(self, name, api):
        """Constructor."""
        super(Templates, self).__init__(name, api)
        self.collection = self.__collection_name__
        self.type = self.cloud_type + '::Template'

    def get_resource(self, name):
        """Override the parent get_resource."""
        val = super(Templates, self).get_resource(name)
        if val is None:
            log.abort('Template %s not found for provider %s.' %
                      (name, self.name))
        return val

    def get_id(self, name):
        """Override the parent get_id."""
        return self.get_resource(name)['guid']


class SecurityGroups(Provider):
    """Provider security group component."""

    __collection_name__ = 'security_groups'

    def __init__(self, name, api):
        """Constructor."""
        super(SecurityGroups, self).__init__(name, api)
        self.collection = self.__collection_name__
        self.type = self.network_type + '::SecurityGroup'

    def get_resource(self, name):
        """Override the parent get_resource."""
        val = super(SecurityGroups, self).get_resource(name)
        if val is None:
            log.abort('Security group %s not found for provider %s.' %
                      (name, self.name))
        return val


class KeyPair(Provider):
    """Provider key pair component."""

    __collection_name__ = 'authentications'

    def __init__(self, name, api):
        super(KeyPair, self).__init__(name, api)
        self.collection = self.__collection_name__
        self.type = self.cloud_type + '::AuthKeyPair'

    def get_resource(self, name):
        """Override the parent get_resource."""
        val = super(KeyPair, self).get_resource(name)
        if val is None:
            log.abort('Key pair %s not found for provider %s.' %
                      (name, self.name))
        return val


class Tenant(Provider):
    """Provider tenant component."""

    __collection_name__ = 'cloud_tenants'

    def __init__(self, name, api):
        """Constructor."""
        super(Tenant, self).__init__(name, api)
        self.collection = self.__collection_name__
        self.type = self.cloud_type + '::CloudTenant'

    def get_resource(self, name):
        """Override the parent get_resource."""
        val = super(Tenant, self).get_resource(name)
        if val is None:
            log.abort('Tenant %s not found for provider %s.' %
                      (name, self.name))
        return val


class Networks(Provider):
    """Provider network component."""

    __collection_name__ = 'cloud_networks'

    def __init__(self, name, api, network=None):
        """Constructor."""
        super(Networks, self).__init__(name, api)
        self.collection = self.__collection_name__
        if network and network is not None :
            self.type = self.network_type + '::CloudNetwork::' + network.title()
        else:
            self.type = self.network_type + '::CloudNetwork'

    def get_resource(self, name):
        """Override the parent get_resource."""
        val = super(Networks, self).get_resource(name)
        if val is None:
            log.abort('Network %s not found for provider %s.' %
                      (name, self.name))
        return val
