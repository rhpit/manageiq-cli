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

__all__ = ['info', 'debug', 'error', 'warning', 'abort']


def __log(message, level, bold=False, fg=None):
    """Base function to log messages using click library.

    Function is private and not visible from other modules. Modules should
    use the logging level functions to log messages.

    :param message: Message content
    :type message: str
    :param level: Logging level
    :type level: str
    :param bold: Bold style text
    :type bold: bool
    :param fg: Text foreground color
    :type fg: str
    """
    click.secho('{0}: {1}'.format(level.upper(), message), bold=bold, fg=fg)


def info(message):
    """Info level messages.

    Info messages should be used when the program needs to provide the user
    with information at runtime. I.e. providing the user with a message
    stating which action is being processed, etc..

    :param message: Message to print
    :type message: str
    """
    __log(message, 'info')


def debug(message):
    """Debug level messages.

    Debug messages should be used when the program wants to provide the
    user with more information at runtime. These can be good for explaining
    step by step a request being processed (if the user wishes to see the
    process). These messages by default will not be logged and only will be
    logged when --verbose option is enabled.

    :param message: Message content
    :type message: str
    """
    if click.get_current_context().find_root().params['verbose']:
        __log(message, 'debug')


def error(message):
    """Error level messages.

    Error messages should be used when the program needs to alert the user
    when something went wrong. I.e. a request was unable to be processed,
    connection failed, etc..

    :param message: Message content
    :type message: str
    """
    __log(message, 'error', bold=True, fg='red')


def warning(message):
    """Logs warning level messages.

    Warning messages should be used when the program needs to alert the user
    that it may not function as designed. I.e. user did not supply the
    correct values, etc..

    :param message: Message content
    :type message: str
    """
    __log(message, 'warning', fg='yellow')


def abort(message, rc=1):
    """Logs error level message and aborts the program.

    Abort should be self explanatory. It will abort the program when it is
    unable to proceed processing the request given.

    :param message: Message content
    :type message: str
    :param rc: Exit code to abort with
    :type rc: int
    """
    error(message)
    raise SystemExit(rc)
