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

from miqcli.cli.collection import Collection


class Collections(Collection):
    """Instances collections."""

    def query(self):
        """Query."""
        raise NotImplementedError

    def terminate(self):
        """Terminate."""
        raise NotImplementedError

    def stop(self):
        """Stop."""
        raise NotImplementedError

    def start(self):
        """Start."""
        raise NotImplementedError

    def pause(self):
        """Pause."""
        raise NotImplementedError

    def suspend(self):
        """Suspend."""
        raise NotImplementedError

    def shelve(self):
        """Shelve."""
        raise NotImplementedError

    def reboot_guest(self):
        """Reboot guest."""
        raise NotImplementedError

    def reset(self):
        """Reset."""
        raise NotImplementedError
