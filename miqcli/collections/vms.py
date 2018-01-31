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

from miqcli.decorators import client_api


class Collections(object):
    """Virtual machines collections."""

    @client_api
    def query(self):
        """Query."""
        raise NotImplementedError

    @client_api
    def edit(self):
        """Edit."""
        raise NotImplementedError

    @client_api
    def add_lifecycle_event(self):
        """Add lifecycle event."""
        raise NotImplementedError

    @client_api
    def add_event(self):
        """Add event."""
        raise NotImplementedError

    @client_api
    def refresh(self):
        """Refresh."""
        raise NotImplementedError

    @client_api
    def shutdown_guest(self):
        """Shutdown guest."""
        raise NotImplementedError

    @client_api
    def reboot_guest(self):
        """Reboot guest."""
        raise NotImplementedError

    @client_api
    def start(self):
        """Start."""
        raise NotImplementedError

    @client_api
    def stop(self):
        """Stop."""
        raise NotImplementedError

    @client_api
    def suspend(self):
        """Suspend."""
        raise NotImplementedError

    @client_api
    def shelve(self):
        """Shelve."""
        raise NotImplementedError

    @client_api
    def shelve_offload(self):
        """Shelve offload."""
        raise NotImplementedError

    @client_api
    def pause(self):
        """Pause."""
        raise NotImplementedError

    @client_api
    def request_console(self):
        """Request console."""
        raise NotImplementedError

    @client_api
    def reset(self):
        """Reset."""
        raise NotImplementedError

    @client_api
    def retire(self):
        """Retire."""
        raise NotImplementedError

    @client_api
    def set_owner(self):
        """Set owner."""
        raise NotImplementedError

    @client_api
    def set_ownership(self):
        """Set ownership."""
        raise NotImplementedError

    @client_api
    def scan(self):
        """Scan."""
        raise NotImplementedError

    @client_api
    def delete(self):
        """Delete."""
        raise NotImplementedError

    @client_api
    def assign_tags(self):
        """Assign tags."""
        raise NotImplementedError

    @client_api
    def unassign_tags(self):
        """Unassign tags."""
        raise NotImplementedError
