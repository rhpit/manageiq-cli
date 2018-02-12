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


class Collections(CollectionsMixin):
    """Blueprints collections."""

    @client_api
    def query(self):
        """Query."""
        raise NotImplementedError

    @client_api
    def create(self):
        """Create."""
        raise NotImplementedError

    @client_api
    def edit(self):
        """Edit."""
        raise NotImplementedError

    @client_api
    def publish(self):
        """Publish."""
        raise NotImplementedError

    @client_api
    def delete(self):
        """Delete."""
        raise NotImplementedError
