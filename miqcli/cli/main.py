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
from copy import copy
from functools import wraps

import click
from os import listdir

from miqcli.api import ClientAPI
from miqcli._compat import ServerProxy
from miqcli.constants import CFG_DIR, CFG_NAME, COLLECTIONS_ROOT, \
    DEFAULT_CONFIG, GLOBAL_PARAMS, PACKAGE, PYPI, VERSION
from miqcli.utils import Config, get_class_methods, log, \
    is_default_config_used, _abort_invalid_commands, get_collection_class


class ManageIQ(click.MultiCommand):
    """ManageIQ command line interface.

    ::
    Class is the main entry point to the miq cli.
    """

    def __init__(self):
        """Constructor."""
        super(ManageIQ, self).__init__(
            context_settings=dict(default_map=DEFAULT_CONFIG),
            help=self.__doc__.split('::')[0].strip(),
            params=GLOBAL_PARAMS
        )

    def list_commands(self, ctx):
        """Return a list of available commands.

        Traverses the collections package to get all module names. Module
        names are the name of the command itself.

        :param ctx: Click context.
        :type ctx: Namespace
        :return: Available commands.
        :rtype: list
        """
        collections = list()
        for filename in listdir(COLLECTIONS_ROOT):
            if '__init__' in filename:
                continue
            if filename.endswith('.py'):
                collections.append(filename[:-3])
        collections.sort()
        return collections

    def get_command(self, ctx, name):
        """Return the command (collections) object based on the command
        selected to run.

        Imports the collection module based on the command to run and gets
        the collection class. The collection class is then passed to the
        sub-command class.

        :param ctx: Click context.
        :type ctx: Namespace
        :param name: Command name.
        :type name: str
        :return: Click command object.
        :rtype: object
        """
        return SubCollections(get_collection_class(ctx, name))

    def invoke(self, ctx):
        """Invoke the command selected.

        Runs the command given with all its arguments. When no command is
        given it will display the cli with all commands/options. This method
        also checks for the version parameter. When given it will display
        version information about the cli.

        :param ctx: Click context.
        :type ctx: Namespace
        """
        if ctx.params.get('version', False):
            # miq cli version
            msg, version = '', ''

            # get ManageIQ CLI available versions from PYPI
            pypi = ServerProxy(PYPI)
            versions = pypi.package_releases(PACKAGE)

            # lets begin version message formatting
            try:
                version_index = versions.index(VERSION)
                if version_index == 0:
                    status = 'an up-to-date'
                else:
                    status = 'an out-of-date'
            except ValueError:
                status = 'a pre-release'

            # lets finalize version message formatting
            try:
                version = versions[0]
            except IndexError:
                version = 'N/A'
            finally:
                msg = 'Installed version : {0}\nLatest version    : {1}\n\n' \
                      'You are running {2} version of ManageIQ CLI!'. \
                    format(VERSION, version, status)
                click.echo(msg)
                ctx.exit()
        else:
            # invoke the collection
            super(ManageIQ, self).invoke(ctx)


class SubCollections(click.MultiCommand):
    """Sub-collections.

    Class handles creating the click sub-command for the given parent command
    (collection) with all its provided options, e.g.::

        miqcli <parent_command> <sub_command>
    """

    def __init__(self, collection_cls):
        """Constructor.

        :param collection: Collection class.
        :type collection: class
        """
        super(SubCollections, self).__init__(help=collection_cls.__doc__)
        self.collection_cls = collection_cls

    def list_commands(self, ctx):
        """Return a list of available sub-commands for the parent command.

        Traverses the collection class to get all method names. Class method
        names are the names of the sub-commands for the parent command.
        """
        return get_class_methods(self.collection_cls)

    @staticmethod
    def convert_to_function(method):
        """Convert an instancemethod to a function.

        :param method: Instancemethod.
        :type method: object
        :return: Function.
        :rtype: object
        """
        @wraps(method)
        def func(*args, **kwargs):
            """Convert instancemethod to a function.

            :param args: Arguments.
            :type args: dict
            :param kwargs: Named arguments.
            :type kwargs: dict
            :return: Function.
            :rtype: object
            """
            return method(*args, **kwargs)
        return func

    def get_command(self, ctx, name):
        """Return the command object for the sub-command for the given parent
        to run.

        Collects the sub-commands options and sets up all needed attributes.
        Then creates a new click command to return to be run.

        :param ctx: Click context.
        :type ctx: Namespace
        :param name: Sub-command name.
        :type name: str
        :return: Click command object.
        :rtype: object
        """
        collection = self.collection_cls()

        method = getattr(collection, name)
        new_method = self.convert_to_function(method)

        params = getattr(method, '__click_params__', [])
        new_method.__click_params__ = copy(params)

        attributes = dict()
        try:
            # removes methods documented parameters from showing in help
            attributes['help'] = method.__doc__.split('::')[0].strip()
        except AttributeError:
            # methods docstring does not container documented parameters
            attributes['help'] = method.__doc__

        cmd = click.command(name=name, **attributes)(new_method)
        return cmd

    def invoke(self, ctx):
        """Invoke the sub-command selected.

        This is where things start to get real. We load configuration
        settings based on the order preference, update the click context with
        the final configuration settings, connect to the ManageIQ server and
        then invoke the command.

        When the help parameter is given for any sub-command, we do not
        attempt connection to ManageIQ server. Only show params and exit.

        :param ctx: Click context.
        :type ctx: Namespace
        """
        # first lets make sure the sub-command given is valid
        if ctx.protected_args[0] not in self.list_commands(ctx):
            _abort_invalid_commands(ctx, ctx.protected_args[0])

        if '--help' not in ctx.args:
            # get parent context
            parent_ctx = click.get_current_context().find_root()

            # create config object
            config = Config(verbose=parent_ctx.params['verbose'])

            # load config settings in the following order:
            #   1. Default configuration settings
            #       - managed by ManageIQ CLI constants
            #   2. CLI parameters
            #       - $ miqcli --options
            #   3. YAML configuration @ /etc/miqcli/miqcli.[yml|yaml]
            #   4. YAML configuration @ ./miqcli.[yml|yaml]
            #   5. Environment variable
            #       - $ export MIQ_CFG="{'key': 'val'}"
            config.from_yml(CFG_DIR, CFG_NAME)
            config.from_yml(os.path.join(os.getcwd()), CFG_NAME)
            config.from_env('MIQ_CFG')

            # set the final parameters after loading config settings
            click.get_current_context().find_root().params.update(
                dict(config)
            )

            # notify user if default config is used
            if is_default_config_used():
                log.warning('Default configuration is used.')

            # create the client api object
            client = ClientAPI(click.get_current_context().find_root().params)

            # connect to manageiq server
            client.connect()

            # save the client api pointer reference in the parent context for
            # each collection to access
            setattr(parent_ctx, 'client_api', client)
            del parent_ctx

        super(SubCollections, self).invoke(ctx)


# it all begins here..
cli = ManageIQ()
