# Copyright (C) 2018 Red Hat, Inc.
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

"""
Demo script used to add Amazon provider.

How to run:
    1. Install manageiq-cli
        - $ pip install -e .
    2. Set the required environment variables
        - AWS_REGION
        - AWS_ZONE
        - AWS_USERNAME
        - AWS_PASSWORD
    3. Run script
        - $ python ./create.py
"""

import os

from miqcli import Client
from miqcli.constants import DEFAULT_CONFIG

REGION = os.getenv('AWS_REGION')
ZONE = os.getenv('AWS_ZONE')
USERNAME = os.getenv('AWS_USERNAME')
PASSWORD = os.getenv('AWS_PASSWORD')


def main():
    client = Client(DEFAULT_CONFIG)
    client.collection = 'providers'

    client.collection.create(
        'Amazon',
        region=REGION,
        zone=ZONE,
        username=USERNAME,
        password=PASSWORD
    )


if __name__ == '__main__':
    main()
