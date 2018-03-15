import os
import stat
import pkgutil

import requests
from unittest import TestCase
from nose.tools import assert_equal

class TestCollections(TestCase):
    """Test Collections module"""

    def setUp(self):

        # I want a list of all valid collections from the appliance
        r = requests.get('https://localhost:8443/api', auth=('admin', 'smartvm'), verify=False)
        self.appliance_collections = [c['name'] for c in r.json()['collections']]

    def tearDown(self):
        del(self.appliance_collections)

    def test_collection_representation_from_appliances(self):
        # test if CLI collections matches appliance collections
        import miqcli.collections
        colpath = os.path.dirname(miqcli.collections.__file__)
        client_collections = [name for _, name, _ in pkgutil.iter_modules([colpath])]
        assert_equal(len(client_collections), len(self.appliance_collections))
        dif = [item for item in client_collections if item not in appliance_collections]
        assert_equal(len(dif), 0)
