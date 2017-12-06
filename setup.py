#!/usr/bin/env python

from setuptools import find_packages, setup

from miqcli.constants import PACKAGE, VERSION

setup(
    name=PACKAGE,
    description='ManageIQ command line interface',
    version=VERSION,
    packages=find_packages('.'),
    install_requires=['click==6.7'],
    setup_requires=['pbr'],
    pbr=True,
    entry_points={'console_scripts': ['{0}={0}.cli.main:cli'.format(PACKAGE)]}
)
