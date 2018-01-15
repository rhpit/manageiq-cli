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

"""Decorator module contains decorators used throughout the cli modules."""

from functools import wraps

from miqcli.utils import get_client_api_pointer


def client_api(method):
    """Client API decorator.

    :param method: Collection method
    :type method: object
    :return: The wrapper function
    """
    @wraps(method)
    def func(*args, **kwargs):
        """Invoke the given collection method.

        Before calling the method, it will set a new collection attribute.
        This attribute is the manageiq client api pointer. This attribute
        will be used to perform requests using the client api library to
        the server. This removes the need for the class to get the object
        from the click context and then use it.

        :param args: Arguments
        :type args: tuple
        :param kwargs: Keyword arguments
        :type kwargs: dict
        :return: The invoked collection method
        """
        setattr(args[0], 'api', get_client_api_pointer())
        return method(*args, **kwargs)
    return func
