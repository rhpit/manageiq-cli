from miqcli import api

from unittest import TestCase
from nose.tools import assert_is_none, assert_equal


class TestApi(TestCase):
    """Test API module"""

    def setUp(self):
        self.cli_emptysettings = api.ClientAPI({})
        self.cli_mocksettings = api.ClientAPI({
            'token': 'abcd1234',
            'username': 'johnny',
            'password': 'p4ssw0rd',
            'url': 'https://mydomain.com'
        })

    def tearDown(self):
        del(self.cli_emptysettings)
        del(self.cli_mocksettings)

    def test_clientapi_empty_settings(self):
        """Test api.ClientAPI with empty parameters"""
        assert_is_none(self.cli_emptysettings._client)
        assert_equal(self.cli_emptysettings._username, 'admin')
        assert_equal(self.cli_emptysettings._password, 'smartvm')
        assert_equal(self.cli_emptysettings._url, 'https://localhost:8443/api')
        assert_equal(self.cli_emptysettings._verify_ssl, False)
        assert_equal(self.cli_emptysettings._token, None)

    def test_clientapi_empty_settings_token_property(self):
        """Test api.ClientAPI.token property with empty parameters"""
        assert_is_none(self.cli_emptysettings._client)
        assert_equal(self.cli_emptysettings._token, None)
        assert_equal(self.cli_emptysettings.token, None)

    def test_clientapi_token_property(self):
        """Test api.ClientAPI.token property with empty parameters"""
        assert_is_none(self.cli_emptysettings._client)
        assert_equal(self.cli_emptysettings._token, None)
        assert_equal(self.cli_emptysettings.token, None)

    def test_clientapi_token_property_from_settings(self):
        """Test api.ClientAPI.token property from mock settings"""
        assert_is_none(self.cli_mocksettings._client)
        assert_equal(self.cli_mocksettings.token, 'abcd1234')

    def test_clientapi_username_var_from_settings(self):
        """Test api.ClientAPI var _username from mock settings"""
        assert_is_none(self.cli_mocksettings._client)
        assert_equal(self.cli_mocksettings._username, 'johnny')

    def test_clientapi_password_var_from_settings(self):
        """Test api.ClientAPI var _password from mock settings"""
        assert_is_none(self.cli_mocksettings._client)
        assert_equal(self.cli_mocksettings._password, 'p4ssw0rd')
