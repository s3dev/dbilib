#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:App:       setup.py
:Purpose:   Python library packager.

:Version:   0.2.1
:Platform:  Linux/Windows | Python 3.6+
:Developer: J Berendt
:Email:     support@s3dev.uk

:Example:
    Create source and wheel distributions::

        $ cd /path/to/package
        $ python setup.py sdist bdist_wheel

    Simple installation::

        $ cd /path/to/package/dist
        $ pip install <pkgname>-<...>.whl

    git installation::

        $ pip install git+file:///<drive>/path/to/package

    github installation::

        $ pip install git+https://github.com/s3dev/<pkgname>

"""
# pylint: disable=too-few-public-methods

import os
from setuptools import setup, find_packages
from dblib._version import __version__


class Setup:
    """Create a dist package for this library."""

    PACKAGE         = 'dblib'
    VERSION         = __version__
    PLATFORMS       = 'Python 3.6+'
    DESC            = 'Generalised and simple database interface library.'
    AUTHOR          = 'J. Berendt'
    AUTHOR_EMAIL    = 'development@s3dev.uk'
    URL             = 'n/a'
    LICENSE         = 'MIT'
    MIN_PYTHON      = '>=3.6'
    ROOT            = os.path.realpath(os.path.dirname(__file__))
    PACKAGE_ROOT    = os.path.join(ROOT, PACKAGE)
    INCL_PKG_DATA   = False
    CLASSIFIERS     = ['Programming Language :: Python :: 3.6',
                       'Programming Language :: Python :: 3.7',
                       'Programming Language :: Python :: 3.8',
                       'Programming Language :: Python :: 3.9',
                       'Programming Language :: Python :: 3.10',
                       'License :: OSI Approved :: MIT License',
                       'Operating System :: Microsoft :: Windows',
                       'Operating System :: POSIX :: Linux',
                       'Topic :: Software Development',
                       'Topic :: Software Development :: Libraries',
                       'Topic :: Utilities']

    # PACKAGE REQUIREMENTS
    REQUIRES        = ['pandas', 'sqlalchemy', 'utils4']
    PACKAGES        = find_packages()

    # ADD DATA AND DOCUMENTATION FILES
    PACKAGE_DATA    = {}

    def run(self):
        """Run the setup."""
        setup(name=self.PACKAGE,
              version=self.VERSION,
              platforms=self.PLATFORMS,
              description=self.DESC,
              python_requires=self.MIN_PYTHON,
              author=self.AUTHOR,
              author_email=self.AUTHOR_EMAIL,
              maintainer=self.AUTHOR,
              maintainer_email=self.AUTHOR_EMAIL,
              url=self.URL,
              license=self.LICENSE,
              packages=self.PACKAGES,
              install_requires=self.REQUIRES,
              include_package_data=self.INCL_PKG_DATA,
              classifiers=self.CLASSIFIERS,
              package_data=self.PACKAGE_DATA)

if __name__ == '__main__':
    Setup().run()
