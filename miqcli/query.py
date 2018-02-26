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

from manageiq_client.api import APIException
from manageiq_client.filters import Q
from miqcli.utils import log

__all__ = ['BasicQuery', 'AdvancedQuery', 'inject']


def inject(lst, item):
    result = [item] * (len(lst) * 2 - 1)
    result[0::2] = lst
    return result


class BaseQuery(object):
    """Base query.

    This class contains default methods each child query class can use.
    """

    def __init__(self, collection):
        """Constructor.

        :param collection: collection object
        :type collection: object
        """
        self.collection = collection
        self.resources = list()

    def __getattr__(self, attr):
        """Return the value for the given attribute.

        :param attr: attribute name
        :type attr: str
        :return: attribute value
        """
        if len(self.resources) == 0:
            raise AttributeError('No available resources. Did you perform '
                                 'a query?')
        elif len(self.resources) == 1:
            # load attributes into entity object
            self.resources[0].reload()

            if attr not in self.resources[0].__dict__:
                raise AttributeError('No such attribute {0}'.format(attr))
            return self.resources[0].__dict__[attr]
        else:
            raise AttributeError('Cannot get attribute when multiple '
                                 'resources exist.')


class BasicQuery(BaseQuery):
    """Basic query.

    This class will perform a basic query on the given collection.
    """

    def __init__(self, collection):
        """Constructor.

        :param collection: collection object
        :type collection: object
        """
        super(BasicQuery, self).__init__(collection)

    def __call__(self, query, attr=None):
        """Performs a basic query on a collection.

        :param query: query containing name, operand and value
        :type query: tuple
        :return: collection resources matching the supplied query
        :rtype: list

        Usage:

        .. code-block: python

            # query vms collection to find the following vm by name
            query = BasicQuery(vm_collection)
            query(('name', '=', 'vm_foo'))
            # -- or --
            query.__call__(('name', '=', 'vm_foo'))
        """
        if len(query) != 3:
            log.warning('Query must contain three indexes. i.e. '
                        '(name, operand, value)')
            return self.resources

        try:
            resources = getattr(self.collection, 'filter')(
                Q(query[0], query[1], query[2])
            )

            self.resources = resources.resources

            if attr:
                for ent in resources.resources:
                    ent.reload(True, True, attr)

        except (APIException, ValueError) as e:
            log.error('Query attempted failed: {0}, error: {1}'.format(
                query, e))

        return self.resources


class AdvancedQuery(BaseQuery):
    """Advanced query.

    This class will perform a advanced query on the given collection
    """

    def __init__(self, collection):
        """Constructor.

        :param collection: collection object
        :type collection: object
        """
        super(AdvancedQuery, self).__init__(collection)

    def __call__(self, query, attr=None):
        """Performs a advanced query on a collection.

        :param query: multiple queries containing name, operand and value
        :type query: list
        :return: collection resources matching the supplied query
        :rtype: list

        Usage:

        .. code-block: python

        query = AdvancedQuery(vm_collection)
        query([('name', '=', 'vm_foo'), '&', ('id', '>', '9999934')])
        # -- or --
        query.__call__([('name', '=', 'vm_foo'), '&', ('id', '>', '9999934')])
        """
        adv_query = ''

        if len(query) % 2 == 0:
            log.warning('Query attempted is invalid: {0}'.format(query))
            return self.resources

        # build query in string form
        while query:
            _query = query.pop(0)

            if isinstance(_query, tuple) and len(_query) != 3:
                log.warning('Query must contain three indexes (name, operator,'
                            ' value)')
                return self.resources
            elif isinstance(_query, tuple):
                adv_query += str("Q('" + str(_query[0]) + "', '" + str(
                    _query[1])) + "', '" + str(_query[2]) + "')"
            elif isinstance(_query, str):
                adv_query += ' {0} '.format(_query)

        try:
            resources = getattr(self.collection, 'filter')(eval(adv_query))

            self.resources = resources.resources

            if attr:
                for ent in resources.resources:
                    ent.reload(True, True, attr)

        except (APIException, ValueError, TypeError) as e:
            # most likely user passed an invalid attribute name
            log.error('Query attempted failed: {0}, error: {1}'.format(
                query, e))

        return self.resources
