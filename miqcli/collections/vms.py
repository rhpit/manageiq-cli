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
from miqcli.api import ClientAPI


class Collections(object):
    """Virtual machines collections."""

    @client_api
    def query(self):
        """Query."""
        print self.api
        print self.all
        print self.api.basic_query(self.collection, [])
        print self.api.basic_query(self.collection, ("id", "=", 429))[0].name
        # test an invalid operator
        self.api.basic_query(self.collection, ("id", "+", 429))
        print self.api.get_collection("")
        print self.api.get_collection("aksdljfdlsk")
        print self.api.advanced_query(self.collection, [("id", "=", 429), "&", ("name", "=", "str-rhel-client-2")])
        print "advanced Query complete"
        print "invalid advanced query 1"
        print self.api.advanced_query(self.collection, [("id", "=", 429), "&"])
        print "invlaid advanced query 2"
        print self.api.advanced_query(self.collection, [("id", "=", 429), ("name", "=", "str-rhel-client-2")])
        print "invalid advanced query 3"
        print self.api.advanced_query(self.collection, [("id", "=", 429), "+", ("name", "=", "str-rhel-client-2")])
        print "invalid advanced query 4"
        print self.api.advanced_query(self.collection, [()])
        found_instance = self.api.basic_query(self.api.get_collection("instances"), ('name', '=', 'jslave-CT-HW-parted-example-parted-a7c35'))[0]
        print found_instance
        del_result = found_instance.action.terminate()
        print del_result
        print del_result._data["task_id"]
        task_id = del_result._data['task_id']
        tasklist = self.api.basic_query(self.api.get_collection("tasks"), ("id", "=", task_id))
        print "got here"
        print tasklist
        return_tuple = self.api.check_task(task_id, "attempt to delete an instance")
        print return_tuple
        #negative test pass an invalid task id
        return_tuple = self.api.check_task(435798347589376593, "attempt to delete a non existant instance")
        print return_tuple

        provision_payload = {'vm_fields': {'vm_name': 'miq-test_machine-vp1', 'cloud_tenant': 3, 'guest_access_key_pair': 6,
                       'instance_type': 58, 'cloud_network': 5, 'placement_auto': 'false', 'security_groups': 5},
         'template_fields': {'guid': '310494ee-d37b-11e7-8df4-0242ac110007'},
         'requester': {'owner_email': 'vipatel@redhat.com'}}

        prov_requests = self.api.get_collection("provision_requests")
        outcome = prov_requests.action.create(provision_payload)
        return_tuple = self.api.check_provision_request(outcome[0].id, "provisioning vm: miq-test_machine-vp1")
        print return_tuple


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
