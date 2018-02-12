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
from manageiq_client.api import APIException
from miqcli.collections import CollectionsMixin
from miqcli.decorators import client_api
from miqcli.query import BasicQuery
from miqcli.utils import log


class Collections(CollectionsMixin):
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

    @click.argument('vm_name', metavar='VM_NAME', type=str, default='')
    @client_api
    def delete(self, vm_name):
        """Delete

        :param vm_name: name of the vm
        :return: id of a task that will delete the vm
        :rtype: int
        """
        if vm_name:
            query = BasicQuery(self.collection)
            vms = query(("name", "=", vm_name))
            if len(vms) < 1:
                log.warning('VM: %s not found!' % vm_name)
                return None
            elif len(vms) > 1:
                # How do we handle deletion when there are multiple matches
                # TODO implement a better solution
                log.warning('Multiple vms with name: '
                            '{0}'.format(vm_name))
                return None
            else:
                try:
                    result = vms[0].action.delete()
                    log.info("Task to delete {0} created: {1}".format(
                        vm_name, result["task_id"]))
                    return result["task_id"]
                except APIException as ex:
                    log.abort('Unable to create a task: delete vm: '
                              '{0}: {1}'.format(vm_name, ex))
        else:
            log.abort('Set an vm name to be deleted.')

    @client_api
    def assign_tags(self):
        """Assign tags."""
        raise NotImplementedError

    @client_api
    def unassign_tags(self):
        """Unassign tags."""
        raise NotImplementedError
