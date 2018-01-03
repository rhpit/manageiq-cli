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

import os

from manageiq_client.api import APIException, ManageIQClient
from requests.exceptions import ConnectionError


class ClientAPI(object):
    """ManageIQ API client class.

    Class interfaces with ManageIQ server. The underlying component performing
    the interactions with the server is the ManageIQ Python API Client.

    https://github.com/ManageIQ/manageiq-api-client-python

    This library is used to establish connection to the server defined, talk
    with all the servers collections and perform CRUD operations.

    Each CLI command will reference this class to perform its collections
    actions.
    """

    def __init__(self):
        """Constructor."""
        self._client = None

    @property
    def client(self):
        """Return the ManageIQ API Client connection property.

        :return: ManageIQ client connection.
        :rtype: object
        """
        return self._client

    @client.setter
    def client(self, value):
        """Set the ManageIQ client connection property.

        :param value: ManageIQ API Client connection
        :type value: object
        """
        self._client = value

    def connect(self, settings):
        """Create a connection to the ManageIQ server.

        :param settings: ManageIQ settings.
        :type settings: dict
        """
        try:
            # TODO: handle setting auth details, covered by issue #33
            self._client = ManageIQClient(
                entry_point=os.path.join(settings['url'], 'api'),
                auth=dict(
                    user=settings['username'],
                    password=settings['password'],
                    token=settings['token']
                ),
                verify_ssl=settings['enable_ssl_verify']
            )
        except (APIException, ConnectionError) as ex:
            raise RuntimeError(ex)
