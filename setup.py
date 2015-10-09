#!/usr/bin/env python

from setuptools import setup
from flutil import __version__

setup(
    name='python-utils',
    version=__version__,
    author='Bryan Johnson',
    author_email='bryan@farmlogs.com',
    packages=['flutil'],
    url='https://github.com/FarmLogs/python-utils',
    download_url='https://github.com/FarmLogs/python-utils/tarball/%s' % __version__,
    install_requires=['psycopg2>=2.6.1', 'tornado==4.0.2', 'Flask==0.10.1']
)
