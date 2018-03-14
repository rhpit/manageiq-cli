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
import urllib3
import errno

from click import Context
from click.globals import push_context

import requests
from requests.auth import HTTPBasicAuth

from manageiq_client.api import APIException, ManageIQClient

from requests.exceptions import ConnectionError

from miqcli.constants import CFG_DIR, CFG_NAME, DEFAULT_CONFIG, TOKENFILE
from miqcli.utils import log, get_collection_class, Config

__all__ = ['ClientAPI', 'Client']

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ClientAPI(object):
    """ManageIQ API client class.

    Class interfaces with ManageIQ server. The underlying component
    performing the interactions with the server is the ManageIQ Python
    API Client.

    https://github.com/ManageIQ/manageiq-api-client-python

    This library is used to establish connection to the server defined,
    talk with all the servers collections and perform CRUD operations.

    Each CLI command will reference this class to perform its
    collections actions.
    """

    def __init__(self, settings):
        """Constructor."""

        # create miqcli folder if it doesn't exist
        try:
            os.makedirs(os.path.dirname(TOKENFILE))
        except OSError as e:
            if e.errno != errno.EEXIST:
                log.abort('Error creating user miqcli folder.')

        # url details
        self._url = settings.get('url', DEFAULT_CONFIG['url'])
        self._url = self._url + '/api'
        self._verify_ssl = settings.get('enable_ssl_verify',
                                        DEFAULT_CONFIG['enable_ssl_verify'])

        # authentication details - username and password should
        # be set in case a given token is invalid.
        self._username = settings.get('username', DEFAULT_CONFIG['username'])
        self._password = settings.get('password', DEFAULT_CONFIG['password'])

        self._token = settings.get('token', None)

        self._client = None

    @property
    def token(self):
        """Token property

        :return: token
        """
        return self._token

    @property
    def client(self):
        """Return the ManageIQ API Client connection property.

        :return: ManageIQ client pointer
        """
        return self._client

    def connect(self):
        """
        Create a connection pointer for the ManageIQ instance. This
        function first build a token to assign it to self._token before
        trying to create a connection pointer.
        """
        self._build_token(token=self.token)
        self._connect()

    def _build_token(self, token=None):
        """
        This function builds and sets the _token property. The user can
        give the token when running the client and, in this case, if
        the token is not valid the function fails and an exception is
        thrown. Otherwise, if the token is not given, the function then
        tries to use what the auth files has. If the token from the
        auth file is not valid or if the file doesn't exist, it will
        create a new token.

        The idea of this function is it will fail only if the user
        provides an invalid token via the command line or if there is
        an error reading the auth file (apart from if the file doesn't
        exist, in this case a file will be created and a valid token
        will be added in the file.

        :param token: given token

        """

        # if none is given
        if token is None:
            # get from auth file and test it
            token = self._get_from_auth_file()

            # if token from auth file is not valid, generate one
            if token is None or not self._valid_token(token):
                token = self._generate_token()
        else:
            # check if given token is valid
            if not self._valid_token(token):
                log.abort('Given token {0} is not valid.'.format(token))

        # always save the token in the auth file
        self._set_auth_file(token)
        self._token = token

    @staticmethod
    def _set_auth_file(token):
        """
        Save the token into TOKENFILE
        :param token: given token
        """
        try:
            with open(TOKENFILE, "w") as fp:
                fp.write(token)
        except (IOError, OSError) as e:
            log.abort('Error setting token file. %s' % e)

    @staticmethod
    def _get_from_auth_file():
        """
        Get the token from the token file (TOKENFILE)
        """
        try:
            with open(TOKENFILE, "r") as fp:
                token = fp.read().strip()
        except IOError as e:
            if e.errno != errno.ENOENT:
                log.abort('Error reading local auth file.')
            return None
        return token

    def _valid_token(self, token=None):
        """
        Check if token is valid. Independently of how the token
        is provided (or not), once the class has a token it will always
        validate it before it is used. In theory, the client will never
        use an invalid token for a sub-command. The only case it may
        happen is that a token expires in between the validation and the
        sub-command execution.

        :param token: given token
        :return: True if token is valid otherwise False
        """
        headers = {'Accept': 'application/json', 'X-Auth-Token': token}
        try:
            output = requests.get(self._url, headers=headers,
                                  verify=self._verify_ssl)
            if output.status_code != 200:
                return False
            return True
        except ConnectionError:
            log.abort('Error connecting to service. Check your connection '
                      'settings.')

    def _generate_token(self):
        """
        Generate a token.

        The idea is that the ClientAPI will try to use a token from a
        given token or from the token saved in the AUTHDIR file.

        Once these first two options failed, it wil then generate a token.
        If a given token or the token from AUTHDIR is still valid
        the username and password is not necessary. In any other case,
        these variables must be set otherwise the function will fail and
        the client will exit with -1.
        """
        if self._username is None or self._password is None:
            log.abort('You need to set username and password.')
        auth_endpoint = self._url + "/auth"
        try:
            output = requests.get(auth_endpoint,
                                  auth=HTTPBasicAuth(self._username,
                                                     self._password),
                                  verify=False)

            if output.status_code == 200:
                return output.json()["auth_token"]
            else:
                log.abort('Unsuccessful attempt to authenticate: '
                          '{0}'.format(output.status_code))
        except ConnectionError:
            log.abort('Error connecting to service. Check your connection '
                      'settings.')

    def _connect(self):
        """
        Create new manageIQClient pointer and assign to self._client
        """
        try:
            self._client = ManageIQClient(self._url,
                                          dict(token=self._token),
                                          verify_ssl=self._verify_ssl)
        except APIException as e:
            log.abort('Error creating library pointer - {0}'.format(e.message))
        except Exception as e:
            log.abort('{0}'.format(e.message))


class Client(object):
    """ManageIQ client class.

    This class is an entry point to accessing the client directly within
    Python modules. Should be used outside the scope of the client source
    code.

    HOW-TO:
    Simply create an instance of the class with your server settings. Then all
    you need to do is set the collection to use and call one of its actions.
    Just like you would via the command line.

    .. code-block: python

        from miqcli import Client

        # create a client object
        client = Client({'url': '', 'username': '', 'password': '', 'etc': ''})

        # set the collection to use
        client.collection = 'providers'

        # call collection action w/params
        client.collection.create(<params>)

    This mirrors the following via command line.

    .. code-block: bash

        miqcli providers create <params>
    """

    _collection = object

    def __init__(self, conf=None, verbose=False):
        """Constructor.

        :param conf: server configuration
        :type conf: dict
        :param verbose: verbose mode
        :type verbose: bool
        """

        # lets first load the correct server configuration settings
        config = Config(settings=DEFAULT_CONFIG, verbose=verbose)
        if conf:
            config.update(conf)
        config.from_yml(CFG_DIR, CFG_NAME)
        config.from_yml(os.path.join(os.getcwd()), CFG_NAME)
        config.from_env('MIQ_CFG')

        # create client api instance
        api = ClientAPI(config)
        api.connect()

        # create click context object (req. for each collection class)
        from miqcli.cli.main import ManageIQ
        self._ctx = Context(ManageIQ())

        # inject req. data into context
        self._ctx.params['verbose'] = verbose
        setattr(self._ctx, 'client_api', api)

        # finally, push context object up the stack for collections to access
        push_context(self._ctx)

    @property
    def collection(self):
        """Collection property.

         :return: collection
         :rtype: class
         """
        return self._collection

    @collection.setter
    def collection(self, name):
        """Set collection property with the instantiated collection class.

        :param name: collection name
        :type name: str
        """
        self._collection = get_collection_class(self._ctx, name)()
