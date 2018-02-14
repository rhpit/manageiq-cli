import os
import stat
import tempfile

from unittest import TestCase
from requests.exceptions import ConnectionError
import mock
from nose.tools import assert_is_none, assert_equal, raises

from miqcli import api

#: token value from tests/assets/auth_token
AUTH_TOKEN_VALUE = '78asdjasd7nasd90asdmzxc90'

#: fake token file
TEMP_AUTH_TOKEN = tempfile.NamedTemporaryFile()

#: fake token file without permission to read
TEMP_AUTH_TOKEN_NOPERMISSION = tempfile.NamedTemporaryFile()
os.chmod(TEMP_AUTH_TOKEN_NOPERMISSION.name, stat.S_IXUSR)

#: fake value to test setting auth token file
FAKE_AUTH_TOKEN_VALUE = 'mkzxcasaaxc87z5zxc5zxc5'


class TestApi(TestCase):
    """Test API module"""

    def setUp(self):
        self.cli_emptysettings = api.ClientAPI({})
        self.cli_withsettings = api.ClientAPI({
            'token': 'abcd1234',
            'username': 'johnny',
            'password': 'p4ssw0rd',
            'url': 'https://mydomain.com'
        })
        self.temp_auth_file = tempfile.NamedTemporaryFile()

    def tearDown(self):
        del(self.cli_emptysettings)
        del(self.cli_withsettings)
        del(self.temp_auth_file)

    @raises(SystemExit)
    @mock.patch('miqcli.api.TOKENFILE', '/root/you/can/doit')
    def test_clientapi_creation_tokenfile_error(self):
        """Test api.ClientAPI creation when auth token can't be created"""
        mycli = api.ClientAPI({})

    def test_clientapi_empty_settings(self):
        """Test api.ClientAPI with empty parameters"""
        assert_is_none(self.cli_emptysettings._client)
        assert_equal(self.cli_emptysettings._username, 'admin')
        assert_equal(self.cli_emptysettings._password, 'smartvm')
        assert_equal(self.cli_emptysettings._url, 'https://localhost:8443/api')
        assert_equal(self.cli_emptysettings._verify_ssl, False)
        assert_equal(self.cli_emptysettings._token, None)

    def test_clientapi_client_property(self):
        """Test api.ClientAPI.client property"""
        assert_equal(
            self.cli_emptysettings._client, self.cli_emptysettings.client)

    def test_clientapi_token_property_empty_settings(self):
        """Test api.ClientAPI.token property without parameters"""
        assert_is_none(self.cli_emptysettings._client)
        assert_equal(self.cli_emptysettings._token, None)
        assert_equal(self.cli_emptysettings.token, None)

    def test_clientapi_token_property_from_settings(self):
        """Test api.ClientAPI.token property with settings"""
        assert_is_none(self.cli_withsettings._client)
        assert_equal(self.cli_withsettings.token, 'abcd1234')

    def test_clientapi_username_var_from_settings(self):
        """Test api.ClientAPI._username property with settings"""
        assert_is_none(self.cli_withsettings._client)
        assert_equal(self.cli_withsettings._username, 'johnny')

    def test_clientapi_password_var_from_settings(self):
        """Test api.ClientAPI._password property with settings"""
        assert_is_none(self.cli_withsettings._client)
        assert_equal(self.cli_withsettings._password, 'p4ssw0rd')

    @mock.patch('miqcli.api.TOKENFILE', TEMP_AUTH_TOKEN.name)
    def test_clientapi_write_tokenfile(self):
        """Test api.ClientAPI._set_auth_file function"""
        self.cli_emptysettings._set_auth_file(FAKE_AUTH_TOKEN_VALUE)
        assert_equal(
            self.cli_emptysettings._get_from_auth_file(), FAKE_AUTH_TOKEN_VALUE)

    @raises(SystemExit)
    @mock.patch('miqcli.api.TOKENFILE', TEMP_AUTH_TOKEN_NOPERMISSION.name)
    def test_clientapi_write_tokenfile_with_no_permission(self):
        """Test api.ClientAPI._set_auth_file when file can't be open"""
        self.cli_emptysettings._set_auth_file(FAKE_AUTH_TOKEN_VALUE)

    @mock.patch('miqcli.api.TOKENFILE', 'tests/assets/auth_token')
    def test_clientapi_read_tokenfile(self):
        """Test api.ClientAPI._get_from_auth_file function"""
        assert_equal(
            self.cli_emptysettings._get_from_auth_file(), AUTH_TOKEN_VALUE)

    @raises(SystemExit)
    @mock.patch('miqcli.api.TOKENFILE', TEMP_AUTH_TOKEN_NOPERMISSION.name)
    def test_clientapi_read_tokenfile_file_no_permission(self):
        """Test api.ClientAPI._get_from_auth_file when file can't be open"""
        self.cli_emptysettings._get_from_auth_file()

    @mock.patch('miqcli.api.TOKENFILE', '/somewhere/not/existent/1234')
    def test_clientapi_read_tokenfile_file_doesnt_exist(self):
        """Test api.ClientAPI._get_from_auth_file when file doesn't exit"""
        assert_is_none(self.cli_emptysettings._get_from_auth_file())

    @mock.patch('requests.get')
    def test_clientapi_validate_token(self, mock_requests_get_func):
        """Test api.ClientAPI._valid_token function"""
        # mock a valid token (response 200)
        mock_requests_get_func.return_value.status_code = 200
        assert_equal(
            self.cli_emptysettings._valid_token(token=FAKE_AUTH_TOKEN_VALUE),
            True)
        # mock an invalid token (response different than 200)
        mock_requests_get_func.return_value.status_code = 401
        assert_equal(
            self.cli_emptysettings._valid_token(token=FAKE_AUTH_TOKEN_VALUE),
            False)

    @mock.patch('miqcli.api.TOKENFILE', 'tests/assets/auth_token')
    @mock.patch('requests.get')
    def test_clientapi_build_token_none_is_given(self, mock_requests_get_func):
        """Test api.ClientAPI._build_token function when none is given"""
        # mock a valid token (response 200)
        mock_requests_get_func.return_value.status_code = 200
        new_client = api.ClientAPI({})
        new_client._build_token()
        assert_equal(new_client.token, AUTH_TOKEN_VALUE)

    @raises(SystemExit)
    @mock.patch('requests.get')
    def test_clientapi_build_token_invalid_is_given(
        self, mock_requests_get_func):
        """Test api.ClientAPI._build_token func when given token is not valid"""
        # mock an invalid token (response 401)
        mock_requests_get_func.return_value.status_code = 401
        new_client = api.ClientAPI({})
        new_client._build_token(token=AUTH_TOKEN_VALUE)

    @raises(SystemExit)
    def test_clientapi_generate_token_none_username(self):
        """Test api.ClientAPI._generate_token when username is none"""
        new_client = api.ClientAPI({'username': None})
        new_client._generate_token()

    @raises(SystemExit)
    def test_clientapi_generate_token_none_password(self):
        """Test api.ClientAPI._generate_token when password is none"""
        new_client = api.ClientAPI({'password': None})
        new_client._generate_token()

    @raises(SystemExit)
    @mock.patch('requests.get')
    def test_clientapi_generate_token_auth_fails(self, mock_requests_get_func):
        """Test api.ClientAPI._generate_token when authentication fails"""
        mock_requests_get_func.return_value.status_code = 401
        new_client = api.ClientAPI({})
        new_client._generate_token()

    @raises(SystemExit)
    @mock.patch('requests.get')
    def test_clientapi_generate_token_conn_error(self, mock_requests_get_func):
        """Test api.ClientAPI._generate_token throws ConnectionError"""
        mock_requests_get_func.side_effect = ConnectionError()
        new_client = api.ClientAPI({})
        new_client._generate_token()
