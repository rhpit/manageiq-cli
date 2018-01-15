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

import os

import click

VERSION = '0.0.0'
PACKAGE = 'miqcli'
PYPI = 'https://pypi.python.org/pypi'
PROJECT_ROOT = os.path.dirname(__file__)
COLLECTIONS_ROOT = os.path.join(PROJECT_ROOT, 'collections')
COLLECTIONS_PACKAGE = PACKAGE + '.' + 'collections'
CFG_DIR = '/etc/miqcli'
CFG_NAME = 'miqcli'
CFG_FILE_EXT = ['.yml', '.yaml']
DEFAULT_CONFIG = {
    'username': 'admin',
    'password': 'smartvm',
    'url': 'https://localhost:8443',
    'enable_ssl_verify': False,
    'verbose': False
}
AUTHDIR = os.path.join(os.path.expanduser('~'), ".miqcli/auth")

GLOBAL_PARAMS = [
    click.Option(
        param_decls=['--version'],
        is_flag=True,
        help='Show version and exit.'
    ),
    click.Option(
        param_decls=['--token'],
        help='Token used for authentication to the server.'
    ),
    click.Option(
        param_decls=['--url'],
        help='URL for the ManageIQ appliance.'
    ),
    click.Option(
        param_decls=['--username'],
        help='Username used for authentication to the server.'
    ),
    click.Option(
        param_decls=['--password'],
        help='Password used for authentication to the server.'
    ),
    click.Option(
        param_decls=['--enable-ssl-verify/--disable-ssl-verify'],
        default=None,
        help='Enable or disable ssl verification, default is on.'
    ),
    click.Option(
        param_decls=['--verbose'],
        is_flag=True,
        help='Verbose mode.'
    )
]
