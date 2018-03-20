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

from miqcli.collections import CollectionsMixin
from miqcli.decorators import client_api
from miqcli.utils import log


class Collections(CollectionsMixin):
    """Zones collections."""

    @client_api
    def query(self):
        """Query."""
        zones = self.all
        log.info('-' * 50)
        log.info('Zones'.center(50))
        log.info('-' * 50)
        for zone in zones:
            log.info(' * ID: %s' % zone['id'])
            log.info(' * Name: %s' % zone['name'])
            log.info(' * Description: %s' % zone['description'])
            log.info('-' * 50)
        return zones
