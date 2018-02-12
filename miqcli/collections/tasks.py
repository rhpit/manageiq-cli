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

import click
from collections import OrderedDict

from miqcli.collections import CollectionsMixin
from miqcli.decorators import client_api
from miqcli.query import BasicQuery
from miqcli.utils import log


class Collections(CollectionsMixin):
    """Tasks collections."""

    @client_api
    def query(self):
        """Query."""
        raise NotImplementedError

    @click.argument('task_id', metavar='ID', type=str, default='')
    @client_api
    def status(self, task_id):
        """Print the status for a provision request.

        ::
        Handles getting information for an existing provision request and
        displaying/returning back to the user.

        :param req_id: id of the provisioning request
        :type req_id: str
        :return: provision request object or list of provision request objects
        """
        status = OrderedDict()
        query = BasicQuery(self.collection)
        if task_id:

            tasklist = query(("id", "=", task_id))

            if len(tasklist) < 1:
                log.warning('Provision request id: %s not found!' % task_id)
                return None

            task = tasklist[0]
            status['state'] = task.state
            status['status'] = task.status
            status['message'] = task.message
            log.info('-' * 50)
            log.info('Tasks'.center(50))
            log.info('-' * 50)
            log.info(' * ID: %s' % task_id)
            log.info(' * Name: %s' % task.name)
            for key, value in status.items():
                log.info(' * %s: %s' % (key.upper(), value))
            log.info('-' * 50)

            return task
        else:
            task_list = query(("state", "!=", "Finished"))

            if len(task_list) < 1:
                log.warning(' * No active tasks at this time')
                return None

            log.info('-' * 50)
            log.info(' Active tasks'.center(50))
            log.info('-' * 50)

            for item in task_list:
                log.info(' * ID: %s\tNAME: %s\tSTATE: %s\tSTATUS: %s' %
                         (item.id, item.name, item.state, item.status))
            log.info('-' * 50)
            return task_list
