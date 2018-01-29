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
import yaml
import ast
import json
from types import FunctionType

import click

from miqcli.constants import CFG_FILE_EXT
from miqcli.utils import log

__all__ = ['Config', 'get_class_methods', 'get_client_api_pointer',
           'is_default_config_used', 'display_commands',
           '_abort_invalid_commands']


class Config(dict):
    """Configuration class."""

    def __init__(self, defaults=None, verbose=False):
        """Constructor.

        :param defaults: base dictionary configuration
        :type defaults: dict
        :param verbose: verbosity mode
        :type verbose: bool
        """
        super(Config, self).__init__(defaults or {})
        self._verbose = verbose

    def from_yml(self, directory, filename):
        """Load configuration settings from yml file.

        :param directory: directory to scan for config file
        :type directory: str
        :param filename: config filename
        :type filename: str
        """
        _cfg_file = None

        # verify config file exists
        for entry in os.listdir(directory):
            _file = os.path.splitext(entry)
            if _file[0] == filename and _file[1] in CFG_FILE_EXT:
                _cfg_file = os.path.join(directory, entry)
                break

        if _cfg_file is None and self._verbose:
            log.warning('Config file at {0} is undefined.'.format(directory))
            return
        if _cfg_file is None:
            return

        # load config
        try:
            with open(_cfg_file, mode='rb') as fp:
                config_data = yaml.load(fp)
                if config_data is not None:
                    for key, value in config_data.items():
                        self[key] = value
                else:
                    log.warning('Config file {0} is empty.'.format(_cfg_file))
        except yaml.YAMLError as e:
            if self._verbose:
                log.debug('Standard error: {0}'.format(e.sterror))
                log.abort('Error in config {0}.'.format(_cfg_file))

    def from_env(self, var):
        """Load configuration settings from environment variable.

        :param var: variable name in dict syntax
        :type var: str
        """
        try:
            for key, value in ast.literal_eval(os.environ[var]).items():
                self[key] = value
        except KeyError:
            if self._verbose:
                log.warning('Config environment variable is undefined.')


def get_class_methods(cls):
    """Return a list of class methods.

    Does a lookup on the given class supplied to round up all methods.

    :param cls: Class to lookup.
    :type cls: class
    :return: List of class methods.
    :rtype: list
    """
    methods = list()

    for key, value in cls.__dict__.items():
        if not isinstance(value, FunctionType):
            continue
        if key == "__init__":
            continue
        methods.append(key)
    methods.sort()
    return methods


def get_client_api_pointer():
    """Return the client api pointer.

    :return: MIQ client api pointer
    :rtype: object
    """
    try:
        return click.get_current_context().find_root().client_api
    except AttributeError:
        log.error('Unable to get client api pointer.')


def is_default_config_used():
    """Is the default configuration used?

    :return: True - defaults used, False - defaults not used
    :rtype: bool
    """
    status = True

    # get parent context
    ctx = click.get_current_context().find_root()

    # compare default config settings with final parameters
    for key, value in ctx.default_map.items():
        if value == ctx.params[key]:
            # option values match
            continue
        else:
            # option values differ
            status = False
            break
    return status


def display_commands(ctx):
    """Displays the available cli commands.

    :param ctx: Click context
    :type ctx: Namespace
    """
    # create clicks formatter object
    formatter = ctx.make_formatter()

    # call clicks method to get and format all available commands
    ctx.command.format_options(ctx, formatter)

    # discard options only leaving commands
    commands = formatter.getvalue().rstrip('\n').split('Commands:')[1]

    print('Commands:\n {0}'.format(commands))


def _abort_invalid_commands(ctx, name):
    """Abort the CLI when an invalid command is supplied.

    :param ctx: Click context
    :type ctx: Namespace
    :param name: Command name
    :type name: str
    """
    display_commands(ctx)
    log.abort('Command "{0}" is invalid. Please choose a valid command '
              'from the list above.'.format(name))


def get_input_data(payload, payload_file):
    """
    helper function to get payload data from a string or json file.
    :param payload: str representation of json payload data
    :param payload_file: json file
    :return:
    """
    if payload:
        try:
            return ast.literal_eval(payload)
        except SyntaxError as e:
            log.abort(e)
    elif payload_file:
        if os.path.isfile(payload_file):
            with open(payload_file) as f:
                try:
                    return json.load(f)
                except ValueError as e:
                    log.abort(e)
        else:
            log.abort("File: {0} not found.".format(payload_file))
    else:
        log.abort("Please set the payload or payload_file")
