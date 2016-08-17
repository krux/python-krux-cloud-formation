# -*- coding: utf-8 -*-
#
# © 2016 Krux Digital, Inc.
#

"""
Package setup for krux-cloud-formation
"""

#
# Standard libraries
#
from __future__ import absolute_import
from setuptools import setup, find_packages

# We use the version to construct the DOWNLOAD_URL.
VERSION = '0.1.1'

# URL to the repository on Github.
REPO_URL = 'https://github.com/krux/python-krux-cloud-formation'
# Github will generate a tarball as long as you tag your releases, so don't
# forget to tag!
DOWNLOAD_URL = ''.join((REPO_URL, '/tarball/release/', VERSION))


setup(
    name='krux-cloud-formation',
    version=VERSION,
    author='Peter Han',
    author_email='phan@krux.com',
    maintainer='Peter Han',
    maintainer_email='phan@krux.com',
    description='Library for updating AWS CloudFormation using troposphere and krux-boto',
    url=REPO_URL,
    download_url=DOWNLOAD_URL,
    license='All Rights Reserved.',
    packages=find_packages(),
    install_requires=[
        'krux-boto',
    ],
    entry_points={
        'console_scripts': [
            'krux-cloud-formation-test = krux_cloud_formation.cli:main',
        ],
    },
    test_suite='test',
)
