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
import errno
import inspect
from time import sleep

import requests
from requests.auth import HTTPBasicAuth

from manageiq_client.api import APIException, ManageIQClient
from manageiq_client.filters import Q

from requests.exceptions import ConnectionError

from miqcli.constants import AUTHDIR, DEFAULT_CONFIG, TASK_WAIT, PROV_REQ_WAIT
from miqcli.utils import log

__all__ = ['ClientAPI']


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
            os.makedirs(os.path.dirname(AUTHDIR))
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
        Save the token into AUTHDIR
        :param token: given token
        """
        try:
            with open(AUTHDIR, "w") as fp:
                fp.write(token)
        except OSError as e:
            log.abort('Error setting token file. %s' % e)

    @staticmethod
    def _get_from_auth_file():
        """
        Get the token from the auth file (AUTHDIR)
        """
        try:
            with open(AUTHDIR, "r") as fp:
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
        output = requests.get(self._url, headers=headers,
                              verify=self._verify_ssl)
        if output.status_code != 200:
            return False
        return True

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

    def get_name(self):
        """
        get the name of the collection module
        :return: name of the collection
        """
        mod_stack = inspect.stack()[2]
        module = inspect.getmodule(mod_stack[0])
        return module.__name__.split(".")[-1]

    def get_collection(self, collection_name=None):
        """
        get the collection object given the name
        :param collection_name: name of the collection
        :return: collection object
        """
        if collection_name:
            try:
                return getattr(self.client.collections, collection_name)
            except AttributeError:
                log.warning("Collection {0} does not exist.".format(
                    collection_name)
                )
                return None
        else:
            name = self.get_name()
            return getattr(self.client.collections, name)

    def basic_query(self, collection, query):
        """
        basic query of a collection object

        Example of the input
        vms, ("name","=","cbn_eap64openjdk17c6_pkcrx")

        :param collection: the collection object to be queried
        :param query: tuple of name, operand, value
        :return: a list of collections from the query
                 (Empty if none or invalid)
        """
        try:
            if (len(query) == 3):
                return collection.filter(
                    Q(query[0], query[1], query[2])
                ).resources
            else:
                log.warning("Invalid query: {0}".format(query))
                return([])
        # ValueError caught for invalid operators used
        except (APIException, ValueError) as e:
            log.warning("Invalid Query attempted: {0}, Error: {1}".format(
                query, e)
            )
            return ([])

    def advanced_query(self, collection, query_list):
        """
        Advance query of a collection object, which just means it is
        a chain of multiple queries with the & or | operands.

        Example of the input:
        "vms", [("name","=","cbn_eap64openjdk17c6_pkcrx"),
        '|', ("id",">",9999934)]

        :param collection:
        :param query_list: list of (name, operand, value) tuples and operands
        :return:
        """
        query = ""
        if len(query_list) % 2 == 0:
            # warning message, invalid query was attempted <query_dict>
            log.warning("Invalid query attempted {0}".format(query_list))
            return ([])
        while (query_list):
            query_tuple = query_list.pop(0)
            # verify the querying tuple has 3 vals set (name, operator, value)
            if (len(query_tuple) == 3):
                query += str("Q('" + str(query_tuple[0]) + "', '" +
                             str(query_tuple[1])) + "', '" + \
                    str(query_tuple[2]) + "')"
            else:
                log.warning("Invalid query: {0}".format(query_tuple))
                return([])
            if query_list:
                query += " {} ".format(query_list.pop(0))
            else:
                try:
                    resources = self.client.collections.instances.filter(
                        eval(query)
                    ).resources
                except (APIException, ValueError, TypeError) as e:
                    # most likely user passed an invalid attribute name
                    error = "Invalid Query attempted: {0}, Error: " \
                            "{1}".format(query, e)
                    log.warning(error)
                    return ([])
                return resources

    def check_task(self, task_id, task_name):
        """
        check_task will keep checking a task until it is complete
        and return if it was successful or not.

        :param task_id: id of the task to check
        :param task_name: message of the task being attempted
        :return: tuple (0/1, message)
        """
        done = False
        while (not done):
            query = ("id", "=", task_id)
            tasklist = self.basic_query(self.client.collections.tasks, query)
            if len(tasklist) == 1:
                task = tasklist[0]
                log.debug("Task state: {0}".format(task.state))
                log.debug("Task status: {0}".format(task.status))
                if task.state == "Finished":
                    done = True
                    if task.status == "Error":
                        return(1, "Task: {0} failed: {1}".format(
                            task_name, task.message))
                # wait for the task to be complete
                sleep(TASK_WAIT)
            else:
                error = "Task not found, query: {0} returned {1}".format(
                    query, tasklist
                )
                log.warning(error)
                return(1, error)

            if not done:
                # update the tasks collection
                self.client.collections.tasks.reload
            else:
                return(0, "Task: {} was successful.".format(task_name))

    def check_provision_request(self, prov_request_id, prov_request_name):
        """
        check_provision_task will keep checking a provision_requests until it
        is complete and return if it was successful or not.
        :param prov_request_id: id of the provision request
        :param prov_request_name: message of the request being attempted
        :return: tuple (0/1, message)
        """

        done = False
        state = ""
        while (not done):
            query = ("id", "=", prov_request_id)
            pro_req_list = self.basic_query(
                self.client.collections.provision_requests,
                query
            )
            if len(pro_req_list) == 1:
                prov_request = pro_req_list[0]
                if prov_request.request_state != state:
                    state = prov_request.request_state
                    log.info(state)
                else:
                    # give user feedback of the progress
                    log.info(".")
                log.debug("Provision Request State: {0}".format(
                    prov_request.request_state)
                )
                log.debug("Provision Request Status: {0}".format(
                    prov_request.status)
                )
                if prov_request.request_state == "finished":
                    done = True
                    if prov_request.status == "Error":
                        return(1, "Provision Task {0} failed {1}".format(
                            prov_request_name, prov_request.message))
                # wait for the request to be updated
                sleep(PROV_REQ_WAIT)
            else:
                error = "Provision Task not found, query: {0} returned " \
                    "{1}".format(query, pro_req_list)
                log.warning(error)
                return(1, error)

            if not done:
                # update the provision requests collection
                self.client.collections.provision_requests.reload
            else:
                return(0, "Task: {} was successful".format(prov_request_name))
