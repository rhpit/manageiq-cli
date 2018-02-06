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

__all__ = ['client_api']


def client_api(method):
    """Client API decorator.

    :param method: Collection method
    :type method: object
    :return: The wrapper function
    """
    @wraps(method)
    def func(*args, **kwargs):
        """Invoke the given collection method.

        Before calling the collection method, it will set common attributes
        that are used by the collection class itself. These attributes
        remove the need to perform lookups within the collection method
        itself.

        :param args: Arguments
        :type args: tuple
        :param kwargs: Keyword arguments
        :type kwargs: dict
        :return: The invoked collection method
        """
        # set the api pointer attribute
        setattr(args[0], 'api', get_client_api_pointer())
        _api = getattr(args[0], 'api')

        # set the api.client.collection pointer attribute
        setattr(args[0], 'collection', getattr(
            _api.client.collections, args[0].__module__.split('.')[-1]))
        _collection = getattr(args[0], 'collection')

        # set the api.client.collection.all attribute
        setattr(args[0], 'all', _collection.all)

        # set the api.client.collection.action pointer attribute
        try:
            setattr(args[0], 'action', getattr(
                _collection.action, method.__name__))
        except (AttributeError, RuntimeError):
            # action does not exist
            setattr(args[0], 'action', None)

        return method(*args, **kwargs)
    return func
