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

__all__ = ['CollectionsMixin']


class CollectionsMixin(object):
    """Mixin collections class.

    Provides extra properties and methods to collections.
    """

    # request id
    _req_id = ''

    @property
    def req_id(self):
        """Request id property.

        :return: request id
        :rtype: str
        """
        return self._req_id

    @req_id.setter
    def req_id(self, value):
        """Set the request id.

        The ManageIQ API Client library's action calls returns its output
        using the built-in 'map'. Python 2 map returns a list of results,
        while Python 3 map returns the iterator itself. This property setter
        handles getting the id.

        Usage

        .. code-block: python

        self.req_id = self.action(<payload>)
        log.info('Request ID: %s.' % self.req_id)

        :param value: request id
        :type value: iterator|list
        """
        try:
            # python 3
            results = next(value)
        except TypeError:
            # python 2
            results = value.pop(0)
        self._req_id = getattr(results, 'id')
