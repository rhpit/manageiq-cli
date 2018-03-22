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
from miqcli.query import AdvancedQuery
from miqcli.query import BasicQuery
from miqcli.query import inject
from miqcli.utils import log


class Collections(CollectionsMixin):
    """Virtual machines collections."""

    @click.option('--by_id', type=bool, default=False,
                  help='name given as ID of vm')
    @click.option('--attr', type=str, default='',
                  help='attribute of a vm(s)', multiple=True)
    @click.option('--provider', type=str, default='',
                  help='provider of an vm(s)')
    @click.option('--vendor', type=str, default='',
                  help='vendor of an vm(s)')
    @click.option('--vtype', type=str, default='',
                  help='type of an vm(s) - ex. "Openstack", "Amazon"...')
    @click.argument('vm_name', metavar="VM_NAME", type=str, default='')
    @client_api
    def query(self, vm_name, provider=None, vendor=None,
              vtype=None, attr=None, by_id=False):
        """Query vms.

        ::
        Allows querying vms based on name, provider and attributes

        :param vm_name: name of the vm
        :type vm_name: str
        :param provider: name of provider
        :type provider: str
        :param vendor: name of vendor
        :type vendor: str
        :param vtype: type of vm - "Openstack" or "Amazon"
        :type vtype: str
        :param attr: attribute
        :type attr: tuple
        :param by_id: name is vm id
        :type by_id: bool
        :return: vm object or list of vm objects
        """
        vms = None

        # Query by ID
        if by_id:
            # ID given in name
            if vm_name:
                # query based on vm name as ID
                # all other options ignored except attr

                qs_by_id = ("id", "=", vm_name)
                query = BasicQuery(self.collection)
                vms = query(qs_by_id, attr)

                if len(vms) < 1:
                    log.abort(
                        'Cannot find Vm with ID:%s in %s' %
                        (vm_name,
                         self.collection.name))

            # Error no ID given
            else:
                log.abort('No Vm ID given')

        # Query by name and other options
        else:
            # Build query string
            qstr = []
            if vm_name:
                qstr.append(("name", "=", vm_name))
            if provider:
                qstr.append(("ext_management_system.name", "=", provider))
            if vendor:
                qstr.append(("vendor", "=", vendor.lower()))
            if vtype:
                type_str = "ManageIQ::Providers::%s::CloudManager::Vm" % vtype
                qstr.append(("type", "=", type_str))

            # Concat together and'ing statements
            qs = inject(qstr, "&")

            # query based on vm name and other options
            if len(qs) > 0:
                if len(qs) == 1:
                    # Name only
                    query = BasicQuery(self.collection)
                    vms = query(qs[0], attr)
                else:
                    # Mix of various options and name
                    query = AdvancedQuery(self.collection)
                    vms = query(qs, attr)

                if len(vms) < 1:
                    log.abort('No Vm(s) found for given parameters')

            # general query on all vms
            else:

                # return vms that have the attribute passed set
                if attr:
                    vms = self.collection.all_include_attributes(attr)

                # attribute not set, pass back all vms w/basic info
                else:
                    vms = self.collection.all

        if vms:
            log.info('-' * 50)
            log.info('Vm Info'.center(50))
            log.info('-' * 50)

            for e in vms:
                log.info(' * ID: %s' % e['id'])
                log.info(' * NAME: %s' % e['name'])

                if attr:
                    for a in attr:
                        try:
                            log.info(' * %s: %s' % (a.upper(), e[a]))
                        except AttributeError:
                            log.info(' * %s: ' % a.upper())
                log.info('-' * 50)

            if len(vms) == 1:
                return vms[0]
            else:
                return vms
        else:
            log.abort('No vm(s) found for given parameters')

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

    @click.option('--by_id', type=bool, default=False,
                  help='name given as ID of vm')
    @click.option('--provider', type=str, default='',
                  help='provider of a vm(s)')
    @click.option('--vendor', type=str, default='',
                  help='vendor of an vm(s)')
    @click.option('--vtype', type=str, default='',
                  help='type of an vm(s) - ex. "Openstack", "Amazon"...')
    @click.argument('vm_name', metavar='VM_NAME', type=str, default='')
    @client_api
    def delete(self, vm_name, provider=None, vendor=None,
               vtype=None, by_id=False):
        """Delete.

        ::
        Delete the vm with the provided options.

        :param vm_name: name of the vm
        :type vm_name: str
        :param provider: name of the provider
        :type provider: str
        :param vendor: name of vendor
        :type vendor: str
        :param vtype: type of vm - "Openstack" or "Amazon"
        :type vtype: str
        :param by_id: name is vm id
        :type by_id: bool
        :return: id of a task that will delete the vm
        :rtype: int
        """
        if vm_name:
            vm = self.query(vm_name, provider, vendor,
                            vtype, by_id=by_id)
            if vm and type(vm) is list:
                log.abort("Multiple vms found."
                          "Supply more options to narrow.")
            try:
                result = vm.action.delete()
                log.info("Task to delete {0} created: {1}".format(
                    vm_name, result["task_id"]))
                return result["task_id"]
            except APIException as ex:
                log.abort('Unable to create a task: delete vm: '
                          '{0}: {1}'.format(vm_name, ex))
        else:
            log.abort('Set a vm to be deleted.')

    @client_api
    def assign_tags(self):
        """Assign tags."""
        raise NotImplementedError

    @client_api
    def unassign_tags(self):
        """Unassign tags."""
        raise NotImplementedError
