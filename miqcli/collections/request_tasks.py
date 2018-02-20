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

from pprint import pformat

import click
from collections import OrderedDict

from miqcli.collections import CollectionsMixin
from miqcli.decorators import client_api
from miqcli.query import BasicQuery
from miqcli.utils import log


class Collections(CollectionsMixin):
    """Request tasks collections."""

    @click.argument('req_id', metavar='ID', type=str, default='')
    @client_api
    def status(self, req_id):
        """Get the status for a request task.

        ::
        Handles getting information for an existing request and
        displaying/returning back to the user.

        :param req_id: id of the request
        :type req_id: str
        :return: request task object or list of request objects
        """
        status = OrderedDict()
        query = BasicQuery(self.collection)

        if req_id:
            requests_tasks = query(("id", "=", req_id))

            if len(requests_tasks) < 1:
                log.warning('Request id: %s not found!' % req_id)
                return None

            req = requests_tasks[0]
            status['state'] = req.state
            status['status'] = req.status
            status['message'] = req.message
            log.info('-' * 50)
            log.info('Request'.center(50))
            log.info('-' * 50)
            log.info(' * ID: %s' % req_id)
            log.info(' * Description: %s' % req['description'])
            for key, value in status.items():
                log.info(' * %s: %s' % (key.upper(), value))
            log.info('-' * 50)

            return req
        else:
            requests_tasks = query(("state", "!=", "finished"))

            if len(requests_tasks) < 1:
                log.warning(' * No active requests tasks at this time')
                return None

            log.info('-' * 50)
            log.info(' Active requests'.center(50))
            log.info('-' * 50)

            for item in requests_tasks:
                log.info(' * ID: %s\tDESCRIPTION: %s\tSTATE: %s\tSTATUS: %s' %
                         (item.id, item.description, item.state, item.status))
            log.info('-' * 50)

            return requests_tasks
