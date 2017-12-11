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


class Collections(object):
    """Services collections."""

    def query(self):
        """Query."""
        raise NotImplementedError

    def create(self):
        """Create."""
        raise NotImplementedError

    def edit(self):
        """Edit."""
        raise NotImplementedError

    def retire(self):
        """Retire."""
        raise NotImplementedError

    def set_ownership(self):
        """Set ownership."""
        raise NotImplementedError

    def delete(self):
        """Delete."""
        raise NotImplementedError

    def start(self):
        """Start."""
        raise NotImplementedError

    def stop(self):
        """Stop."""
        raise NotImplementedError

    def suspend(self):
        """Suspend."""
        raise NotImplementedError

    def assign_tags(self):
        """Assign tags."""
        raise NotImplementedError

    def unassign_tags(self):
        """Unassign tags."""
        raise NotImplementedError

    def add_resource(self):
        """Add resource."""
        raise NotImplementedError

    def remote_all_resources(self):
        """Remove all resources."""
        raise NotImplementedError

    def remove_resource(self):
        """Remove resource."""
        raise NotImplementedError
