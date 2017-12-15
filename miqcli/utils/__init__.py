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
from miqcli.constants import MIQCLI_CFG_NAME
from types import FunctionType


__all__ = ['get_class_methods']


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
