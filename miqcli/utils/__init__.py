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
from types import FunctionType

import click

from miqcli.constants import CFG_FILE_EXT
from miqcli.utils import log

__all__ = ['Config', 'get_class_methods', 'get_client_api_pointer']


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
                log.error('Error in config {0}'.format(_cfg_file), abort=True)

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
        log.error('Unable to get client_api pointer.', abort=True)
