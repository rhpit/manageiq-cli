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
import errno
from miqcli.constants import MIQCLI_CFG_NAME
from types import FunctionType


__all__ = ['get_class_methods']


class Config(dict):
    """
    Config class

    :param dict: dictionary of configuration values
    :type dict: dictionary
    """

    def __init__(self, defaults=None):
        """
        initialize the class
        :param defaults: initial dictionary of value
        :type defaults: dictionary
        """
        dict.__init__(self, defaults or {})

    def from_yaml(self, filename, silent=False):
        """
        import the config data from a yaml file
        :param filename: file path to config
        :type: filename: str of a file path
        :param silent: silent errors or not
        :type silent: Boolean
        :return:
        """
        try:
            with open(filename, mode='rb') as fp:
                config_data = yaml.load(fp)
                for key in config_data:
                    self[key] = config_data[key]
        except yaml.YAMLError as e:
            if silent:
                return False
            raise RuntimeError('Problem to load yaml content from file '
                               '{0}'.format(e.sterror))
        except IOError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                return False
            raise RuntimeError('Unable to load configuration file '
                               '{0}'.format(e.strerror))
        except TypeError as e:
            if silent:
                return False
            raise RuntimeError('Set a valid configuration file to load '
                               '{0}'.format(e.strerror))

    def from_env(self, variable_name, silent=False):
        """
        import the config data from an env variable set as a dictionary
        :param variable_name: name of the env_var
        :type variable_name: str
        :param silent: silent errors or not
        :type silent: Boolean
        :return:
        """
        ev = os.environ.get(variable_name)
        if not ev:
            if silent:
                return False
            raise RuntimeError('The environment variable {0} is not set'
                               ''.format(variable_name))
        config_data = ast.literal_eval(ev)
        for key in config_data:
            self[key] = config_data[key]


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


def check_yaml(file_location):
    """ Check for our yaml config file independent of extension
    :param file_location: location of where to search for the yaml
    :tyep file_location: string
    :return: "exists": true/false and "filepath": file_location
    :rtype: dict
    """

    rdict = {"exists": False, "filepath": None}

    if os.path.isfile(
            "{0}.yaml".format(os.path.join(file_location,
                                           MIQCLI_CFG_NAME))) or \
            os.path.isfile(
            "{0}.yml".format(os.path.join(file_location,
                                          MIQCLI_CFG_NAME))):
        rdict["exists"] = True

        yaml_file = "{0}.yaml".format(os.path.join(
            file_location, MIQCLI_CFG_NAME))
        if not os.path.isfile(yaml_file):
            yaml_file = "{0}.yml".format(os.path.join(
                file_location, MIQCLI_CFG_NAME))
        rdict["filepath"] = yaml_file

    return rdict
