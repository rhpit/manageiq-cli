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

import requests
from requests.auth import HTTPBasicAuth

from manageiq_client.api import APIException, ManageIQClient
from requests.exceptions import ConnectionError

from miqcli.constants import AUTHDIR


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

    def __init__(self, settings):
        """Constructor."""
        self._settings = settings
        self._client = None

    @property
    def settings(self):
        """
        :return: dict of settings
        """
        return self._settings

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

    def connect(self):
        """Create a connection to the ManageIQ server.
        """
        settings = self.settings
        # attempt a connection with a passed token
        if "token" in settings and settings["token"]:
            succ_auth, exception = self.miq_auth(settings["token"])
            if not succ_auth:
                raise RuntimeError("Unable to auth with passed token: "
                                   "{0}".format(exception))
        # check for an auth token file & validate
        if os.path.isfile(AUTHDIR):
            with open(AUTHDIR) as f:
                settings["token"] = f.read().strip()
            succ_auth, exception = self.miq_auth(settings["token"])
            if not succ_auth:
                if "username" in settings and settings["username"] and \
                        "password" in settings and settings["password"]:
                    self.get_token()
                else:
                    raise RuntimeError("Please provide valid "
                                       "credentials to connect")
                succ_auth, exception = self.miq_auth(settings["token"])
                if not succ_auth:
                    raise RuntimeError("Unable to authenticate "
                                       "{0}".format(exception))
        # authenticate and create auth token file if it does not exist
        else:
            if not os.path.exists(os.path.dirname(AUTHDIR)):
                os.makedirs(os.path.dirname(AUTHDIR))

            if "username" in settings and settings["username"] and \
                    "password" in settings and settings["password"]:
                self.get_token()
            else:
                raise RuntimeError("Provide valid credentials to connect")
            succ_auth, exception = self.miq_auth(settings["token"])
            if not succ_auth:
                raise RuntimeError("Authentication failed: "
                                   "{0}".format(exception))

    def get_token(self):
        """
        method to get a token if username/password is set
        """
        auth_endpoint = self.settings["url"] + "/api/auth"
        output = requests.get(auth_endpoint,
                              auth=HTTPBasicAuth(self.settings["username"],
                                                 self.settings["password"]),
                              verify=False)

        if output.status_code == 200:
            self.settings["token"] = output.json()["auth_token"]
        else:
            raise RuntimeError("Unsuccessful attempt to authenticate: "
                               "{}".format(output.status_code))

    def miq_auth(self, token):
        """
        method to authenticate to the ManageIQ Server given a token
        :param token: token to authenticate with
        :return: tuple (successful True/False, and Exception)
        :rtype: (Boolean, str)
        """
        settings = self.settings
        connect_url = settings["url"] + "/api"
        ssl_verify = settings["enable_ssl_verify"]

        try:
            self._client = ManageIQClient(connect_url,
                                          dict(token=settings["token"]),
                                          verify_ssl=ssl_verify)
            # update auth file with token
            with open(AUTHDIR, "w") as f:
                f.write(token)

            return True, None
        except (APIException, ConnectionError) as ex:
            # token is invalid
            return False, ex
