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
from miqcli.decorators import client_api
from miqcli.query import BasicQuery
from miqcli.utils import log


class Collections(object):
    """Instances collections."""

    @click.option('--attr', type=str, default='',
                  help='attribute of an instance(s)')
    @click.argument('inst_name', metavar='INST_NAME', type=str, default='')
    @client_api
    def query(self, inst_name, attr):
        """Query instances.

        ::
        Allows querying instances based on name and attributes

        :param inst_name: name of the instance
        :type inst_name: str
        :param attr: attribute
        :type attr: str
        :return: instance object or list of instance objects
        """

        # query based on instance name
        if inst_name:
            query = BasicQuery(self.collection)
            instance = query(("name", "=", inst_name))

            if len(instance) < 1:
                log.abort('Cannot find %s in %s' % (inst_name,
                                                    self.collection.name))
            if len(instance) > 1:
                log.abort('Multiple matching instances for name: .')
            res = instance[0]

            log.info('-' * 50)
            log.info('Instance Info'.center(50))
            log.info('-' * 50)

            # user passed an attribute for the instance
            if attr:
                try:
                    attr_instance = self.collection(res["id"], attr)
                    attribute = attr_instance[attr]
                except AttributeError:
                    log.abort('Attribute %s not found in Instance %s' %
                              (attr, attr_instance['name']))

                log.info(' * ID: %s' % attr_instance["id"])
                log.info(' * NAME: %s' % attr_instance['name'])
                log.info(' * %s: %s' % (attr.upper(), attribute))
                log.info('-' * 50)
                return attr_instance
            else:
                log.info(' * ID: %s' % res["id"])
                log.info(' * NAME: %s' % res['name'])
                log.info('-' * 50)
                return res

        # general query on all instances
        else:

            # return instances that have the attribute passed set
            if attr:
                found = False
                test = self.collection.all_include_attributes(attr)
                itemlist = []
                for item in test:
                    if attr in item._data and item[attr]:
                        itemlist.append(item)
                        found = True
                        log.info('-' * 50)
                        log.info('Instances with %s:'.format(attr).center(50))
                        log.info('-' * 50)
                        log.info(' * ID: %s\tNAME: %s\t %s: %s' %
                                 (item["id"], item['name'],
                                  attr.upper(), item[attr]))
                        log.info('-' * 50)
                if not found:
                    log.info('No matches for attr: %s in %s' %
                             (attr, self.collection.name))
                    return None
                else:
                    return itemlist

            # attribute not set, pass back all instances w/basic info
            else:
                log.info('-' * 50)
                log.info(' Instances'.center(50))
                log.info('-' * 50)

                for item in self.collection.all:
                    log.info(' * ID: %s\tNAME: %s' %
                             (item["id"], item['name']))
                log.info('-' * 50)
                return self.collection.all

    @click.argument('inst_name', metavar='INST_NAME', type=str, default='')
    @client_api
    def terminate(self, inst_name):
        """Terminate instance.

        :param inst_name: name of the instance
        :type inst_name: str
        :return: id of the task created to terminate the instance
        :rtype: int
        """
        if inst_name:
            query = BasicQuery(self.collection)
            instances = query(("name", "=", inst_name))
            if len(instances) < 1:
                log.abort('Instance: %s not found!' % inst_name)
            elif len(instances) > 1:
                # How do we handle deletion when there are multiple matches?
                log.abort('Multiple matchine instances with name: '
                          '{0}'.format(inst_name))
            else:
                try:
                    result = instances[0].action.terminate()
                    log.info("Task to terminate {0} created: {1}".format(
                        inst_name, result["task_id"]))
                    return result["task_id"]
                except APIException as ex:
                    log.abort('Unable to create a task: terminate instance: '
                              '{0}: {1}'.format(inst_name, ex))
        else:
            log.abort('Set an instance name to be terminated.')

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
