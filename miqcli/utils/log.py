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

__all__ = ['info', 'debug', 'error', 'warning']


def __log(message, level, bold=False, fg=None):
    """Base function to log messages using click library.

    Function is private and not visible from other modules. Modules should
    use the logging level functions to log messages.

    :param message: Message content
    :type message: str
    :param level: Logging level
    :type level: str
    :param bold: Bold style text
    :type bool: bool
    :param fg: Text foreground color
    :type fg: str
    """
    click.secho('{0}: {1}'.format(level.upper(), message), bold=bold, fg=fg)


def info(message):
    """Prints info level messages to the consoles standard output.

    :param message: Message to print
    :type message: str
    """
    __log(message, 'info')


def debug(message):
    """Prints debug level messages.

    :param message: Message content
    :type message: str
    """
    if click.get_current_context().parent.params['verbose']:
        __log(message, 'debug')


def error(message, abort=False, rc=1):
    """Prints error level messages.

    :param message: Message content
    :type message: str
    :param abort: Abort the program
    :type abort: bool
    :param rc: Exit code to abort with
    :type rc: int
    """
    __log(message, 'error', bold=True, fg='red')
    if abort:
        raise SystemExit(rc)


def warning(message):
    """Prints warning level messages.

    :param message: Message content
    :type message: str
    """
    __log(message, 'warning', fg='yellow')
