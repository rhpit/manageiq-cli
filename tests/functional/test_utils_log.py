from unittest import TestCase

import click
from click.testing import CliRunner
from nose.tools import assert_equal
from miqcli.utils import log as miqcli_log

MESSAGE = 'Hello Cloud Users'
INFO_MESSAGE_RESULT = u'INFO: %s\n' % MESSAGE
DEBUG_MESSAGE_RESULT = u'DEBUG: %s\n' % MESSAGE
WARNING_MESSAGE_RESULT = u'WARNING: %s\n' % MESSAGE
ERROR_MESSAGE_RESULT = u'ERROR: %s\n' % MESSAGE
ABORT_MESSAGE_RESULT = u'ERROR: %s\n' % MESSAGE

class TestUtilsLog(TestCase):

  def setUp(self):
    self.runner = CliRunner()

  def test_utilslog_info(self):
    """Test utils.log.info message"""
    @click.command()
    def cli():
        """Print an info message"""
        miqcli_log.info(MESSAGE)

    result = self.runner.invoke(cli)
    assert_equal(result.exception, None)
    assert_equal(INFO_MESSAGE_RESULT, result.output)

  def test_utilslog_debug_without_verbose(self):
    """Test utils.log.debug message without setting verbose"""
    @click.command()
    @click.option('-v', '--verbose', count=True)
    def cli(verbose):
        """Print an info message"""
        miqcli_log.debug(MESSAGE)

    result = self.runner.invoke(cli)
    assert_equal(result.exception, None)
    assert_equal(u'', result.output)

  def test_utilslog_debug_with_verbose(self):
    """Test utils.log.debug message with setting verbose"""
    @click.command()
    @click.option('-v', '--verbose', count=True)
    def cli(verbose):
        """Print an info message"""
        miqcli_log.debug(MESSAGE)

    result = self.runner.invoke(cli, ['--verbose'])
    assert_equal(result.exception, None)
    assert_equal(DEBUG_MESSAGE_RESULT, result.output)

  def test_utilslog_warning(self):
    """Test utils.log.warning message"""
    @click.command()
    def cli():
        """Print an warning message"""
        miqcli_log.warning(MESSAGE)

    result = self.runner.invoke(cli)
    assert_equal(result.exception, None)
    assert_equal(WARNING_MESSAGE_RESULT, result.output)

  def test_utilslog_error(self):
    """Test utils.log.error message"""
    @click.command()
    def cli():
        """Print an error message"""
        miqcli_log.error(MESSAGE)

    result = self.runner.invoke(cli)
    assert_equal(result.exception, None)
    assert_equal(ERROR_MESSAGE_RESULT, result.output)

  def test_utilslog_abort(self):
    """Test utils.log.abort message"""
    @click.command()
    def cli():
        """Print an abort message"""
        miqcli_log.abort(MESSAGE)

    result = self.runner.invoke(cli)
    assert isinstance(result.exception, SystemExit)
    assert_equal(ABORT_MESSAGE_RESULT, result.output)