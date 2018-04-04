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
    """Instances collections."""

    @click.option('--by_id', type=bool, default=False,
                  help='inst_name given as ID of instance, '
                       'all other options except --attr are ignored')
    @click.option('--attr', type=str, default='',
                  help='attribute of an instance(s)', multiple=True)
    @click.option('--provider', type=str, default='',
                  help='provider of an instance(s)')
    @click.option('--network', type=str, default='',
                  help='cloud network of an instance(s)')
    @click.option('--tenant', type=str, default='',
                  help='cloud tenant of an instance(s)')
    @click.option('--subnet', type=str, default='',
                  help='cloud subnet of an instance(s)')
    @click.option('--vendor', type=str, default='',
                  help='vendor of an instance(s)')
    @click.option('--itype', type=str, default='',
                  help='type of an instance(s) - ex. "Openstack", "Amazon"...')
    @click.argument('inst_name', metavar='INST_NAME', type=str, default='')
    @client_api
    def query(self, inst_name, provider=None, network=None, tenant=None,
              subnet=None, vendor=None, itype=None, attr=None, by_id=False):
        """Query instances.

        ::
        Allows querying instances based on name and attributes

        :param inst_name: name of the instance
        :type inst_name: str
        :param provider: name of provider
        :type provider: str
        :param network: name of cloud network
        :type network: str
        :param tenant: name of cloud tentant
        :type tenant: str
        :param subnet: name of cloud subnetwork
        :type subnet: str
        :param vendor: name of vendor
        :type vendor: str
        :param itype: type of instance - "Openstack" or "Amazon"
        :type itype: str
        :param attr: attribute
        :type attr: tuple
        :param by_id: name is instance id
        :type by_id: bool
        :return: instance object or list of instance objects
        """

        instances = None

        # Query by ID
        if by_id:
            # ID given in name
            if inst_name:
                # query based on instance name as ID
                # all other options ignored except attr

                qs_by_id = ("id", "=", inst_name)
                query = BasicQuery(self.collection)
                instances = query(qs_by_id, attr)

                if len(instances) < 1:
                    log.abort(
                        'Cannot find Instance with ID:%s in %s' %
                        (inst_name,
                         self.collection.name))

            # Error no ID given
            else:
                log.abort('No Instance ID given')

        # Query by name and other options
        else:
            # Build query string
            qstr = []
            if inst_name:
                qstr.append(("name", "=", inst_name))
            if provider:
                qstr.append(("ext_management_system.name", "=", provider))
            if network:
                qstr.append(("cloud_networks.name", "=", network))
            if tenant:
                qstr.append(("cloud_tenant.name", "=", tenant))
            if subnet:
                qstr.append(("cloud_subnets.name", "=", subnet))
            if vendor:
                qstr.append(("vendor", "=", vendor.lower()))
            if itype:
                type_str = "ManageIQ::Providers::%s::CloudManager::Vm" % itype
                qstr.append(("type", "=", type_str))

            # Concat together and'ing statements
            qs = inject(qstr, "&")

            # query based on instance name and other options
            if len(qs) > 0:
                if len(qs) == 1:
                    # Name only
                    query = BasicQuery(self.collection)
                    instances = query(qs[0], attr)
                else:
                    # Mix of various options and name
                    query = AdvancedQuery(self.collection)
                    instances = query(qs, attr)

                if len(instances) < 1:
                    log.abort('No instance(s) found for given parameters')

            # general query on all instances
            else:

                # return instances that have the attribute passed set
                if attr:
                    # scrub attr of base attributes
                    opt_lists = self.collection.options()
                    att_list = list(attr)
                    for att in att_list:
                        if att in opt_lists['attributes']:
                            att_list.remove(att)
                    cln_atr = tuple(att_list)

                    instances = self.collection.all_include_attributes(cln_atr)

                # attribute not set, pass back all instances w/basic info
                else:
                    instances = self.collection.all

        if instances:
            log.info('-' * 50)
            log.info('Instance Info'.center(50))
            log.info('-' * 50)

            debug = click.get_current_context().find_root().params['verbose']
            for e in instances:
                log.info(' * ID: %s' % e['id'])
                log.info(' * NAME: %s' % e['name'])

                if debug:
                    for k, v in e['_data'].items():
                        if k == "id" or k == "name" or k in attr:
                            continue
                        try:
                            log.debug(' * %s: %s' % (k.upper(), v))
                        except AttributeError:
                            log.debug(' * %s: ' % k.upper())
                if attr:
                    for a in attr:
                        try:
                            log.info(' * %s: %s' % (a.upper(), e[a]))
                        except AttributeError:
                            log.info(' * %s: ' % a.upper())
                log.info('-' * 50)

            if len(instances) == 1:
                return instances[0]
            else:
                return instances
        else:
            log.abort('No instance(s) found for given parameters')

    @click.option('--by_id', type=bool, default=False,
                  help='inst_name given as ID of instance '
                       'all other options are ignored')
    @click.option('--provider', type=str, default='',
                  help='provider of an instance(s)')
    @click.option('--network', type=str, default='',
                  help='cloud network of an instance(s)')
    @click.option('--tenant', type=str, default='',
                  help='cloud tenant of an instance(s)')
    @click.option('--subnet', type=str, default='',
                  help='cloud subnet of an instance(s)')
    @click.option('--vendor', type=str, default='',
                  help='vendor of an instance(s)')
    @click.option('--itype', type=str, default='',
                  help='type of an instance(s) - ex. "Openstack", "Amazon"...')
    @click.argument('inst_name', metavar='INST_NAME', type=str, default='')
    @client_api
    def terminate(self, inst_name, provider=None, network=None, tenant=None,
                  subnet=None, vendor=None, itype=None, by_id=False):
        """Terminate instance.

        ::

        :param inst_name: name of the instance
        :type inst_name: str
        :param provider: provider of the instance
        :type provider: str
        :param network: name of cloud network
        :type network: str
        :param tenant: name of cloud tentant
        :type tenant: str
        :param subnet: name of cloud subnetwork
        :type subnet: str
        :param vendor: name of vendor
        :type vendor: str
        :param itype: type of instance - "Openstack" or "Amazon"
        :type itype: str
        :param by_id: name is instance id
        :type by_id: bool
        :return: id of the task created to terminate the instance
        :rtype: int
        """
        if inst_name:
            instance = self.query(inst_name, provider, network, tenant,
                                  subnet, vendor, itype, by_id=by_id)
            if instance and type(instance) is list:
                log.abort("Multiple instances found."
                          "Supply more options to narrow.")
            try:
                result = instance.action.terminate()
                log.info("Task to terminate {0} created: {1}".format(
                    inst_name, result["task_id"]))
                return result["task_id"]
            except APIException as ex:
                log.abort('Unable to create a task: terminate instance: '
                          '{0}: {1}'.format(inst_name, ex))
        else:
            log.abort('Set an instance to be terminated.')

    @client_api
    def stop(self):
        """Stop."""
        raise NotImplementedError

    @client_api
    def start(self):
        """Start."""
        raise NotImplementedError

    @client_api
    def pause(self):
        """Pause."""
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
    def reboot_guest(self):
        """Reboot guest."""
        raise NotImplementedError

    @client_api
    def reset(self):
        """Reset."""
        raise NotImplementedError
