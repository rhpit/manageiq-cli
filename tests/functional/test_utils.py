import os
import yaml
from unittest import TestCase

from nose.tools import assert_equal
import click
from click.testing import CliRunner
from mock import patch

from miqcli.utils import Config

VALID_ENVVAR_CONFIG = """
{
  'url': 'https://somewhere:8443',
  'username': 'administrator',
  'password': 'p955w04d',
  'enable_ssl_verify': False
}
"""

INVALID_ENVVAR_CONFIG = """
  url: 'https://somewhere:8443',
  username: 'administrator'
}
"""

class TestUtils(TestCase):

  def setUp(self):
    self.runner = CliRunner()

  def test_utils_config_class(self):
    """Test utils config class is an instance of dict"""

    myconfig = Config()
    myconfig['key_a'] = u'some value'
    myconfig['key_b'] = u'some other value'
    assert isinstance(myconfig, dict)
    assert_equal(myconfig['key_a'], u'some value')
    assert_equal(len(myconfig.keys()), 2)

  def test_utils_load_from_yaml(self):
    """Test utils to load config from yaml file"""
    myconfig = Config()
    myconfig.from_yml('tests/assets/', 'config')
    assert_equal('url' in myconfig, True)
    assert_equal('username' in myconfig, True)
    assert_equal('password' in myconfig, True)
    assert_equal(myconfig['url'], 'https://somewhere:8443')

  def test_utils_load_from_yaml_empty_file(self):
    """Test utils to load config from empty yaml file"""
    @click.command()
    def cli():
      """Simulate click env to get output message"""
      myconfig = Config(verbose=True)
      myconfig.from_yml('tests/assets/', 'empty_config')

    result = self.runner.invoke(cli)
    assert_equal(
      u'WARNING: Config file tests/assets/empty_config.yml is empty.\n',
      result.output)

  def test_utils_load_from_nonexistent_yaml(self):
    """Test utils to load config from non-existent yaml file"""
    myconfig = Config()
    myconfig.from_yml('tests/assets/', 'nonexistent_file')
    assert_equal('url' in myconfig, False)

  def test_utils_load_from_yaml_with_syntax_error_verboseone(self):
    """Test utils to load config from a yaml with syntax error w/ verbose on"""
    @click.command()
    @click.option('-v', '--verbose', count=True)
    def cli(verbose):
      """Simulate click env to get output message"""
      myconfig = Config(verbose=True)
      myconfig.from_yml('tests/assets/', 'error_config')

    result = self.runner.invoke(cli, ['--verbose'])
    assert u'DEBUG: Standard error:' in result.output
    assert u'ERROR: Error in config tests/assets/error_config.yml' in \
      result.output
    assert isinstance(result.exception, SystemExit)

  def test_utils_load_from_yaml_with_syntax_error(self):
    """Test utils to load config from a yaml with syntax error"""
    @click.command()
    def cli():
      """Simulate click env to get output message"""
      myconfig = Config()
      myconfig.from_yml('tests/assets/', 'error_config')

    result = self.runner.invoke(cli)
    assert u'ERROR: Error in config tests/assets/error_config.yml' in \
      result.output
    assert isinstance(result.exception, SystemExit)


  def test_utils_load_from_yaml_with_no_format(self):
    """Test utils to load config from a yaml with no format"""
    @click.command()
    def cli():
      """Simulate click env to get output message"""
      myconfig = Config()
      myconfig.from_yml('tests/assets/', 'noformat_config')

    result = self.runner.invoke(cli)
    assert u'ERROR: Config file tests/assets/noformat_config.yml formatted incorrectly.' in \
      result.output
    assert isinstance(result.exception, SystemExit)

  def test_utils_load_from_nonexistent_yaml_verboseon(self):
    """Test utils to load config from non-existent yaml file w/ verbose on"""
    @click.command()
    def cli():
      """Simulate click env to get output message"""
      myconfig = Config(verbose=True)
      myconfig.from_yml('tests/assets/', 'nonexistent_file')

    result = self.runner.invoke(cli)
    assert_equal(u'WARNING: Config file at tests/assets/ is undefined.\n',
                  result.output)

  @patch.dict(os.environ, {'VALID_ENVVAR_CONFIG': VALID_ENVVAR_CONFIG})
  def test_utils_load_from_env_var(self):
    """Test utils to load config from environment variable"""
    myconfig = Config()
    myconfig.from_env('VALID_ENVVAR_CONFIG')
    assert_equal(myconfig['url'], 'https://somewhere:8443')
    assert_equal(myconfig['username'], 'administrator')
    assert_equal(myconfig['password'], 'p955w04d')
    assert_equal(myconfig['enable_ssl_verify'], False)

  def test_utils_load_from_env_variable_nonexistent(self):
    """Test utils to load config from environment variable that doesn't exist"""
    @click.command()
    def cli():
      """Simulate click env to get output message"""
      myconfig = Config(verbose=True)
      myconfig.from_env('ENVVAR_CONFIG')

    result = self.runner.invoke(cli)
    assert_equal(u'WARNING: Config environment variable is undefined.\n',
                  result.output)

  @patch.dict(os.environ, {'INVALID_ENVVAR_CONFIG': INVALID_ENVVAR_CONFIG})
  def test_utils_load_from_env_variable_invalid(self):
    """Test utils to load config from environment variable that is invalid"""
    @click.command()
    def cli():
      """Simulate click env to get output message"""
      myconfig = Config()
      myconfig.from_env('INVALID_ENVVAR_CONFIG')

    result = self.runner.invoke(cli)
    assert u'ERROR: The syntax of the environment variable content is not valid. Check its content.' in \
      result.output
    assert isinstance(result.exception, SystemExit)
