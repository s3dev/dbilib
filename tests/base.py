#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the superclass which is to be inherited
            by the test-specific modules.

:Platform:  Linux/Windows | Python 3.6+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Reminder:  The testing suite must **not** be deployed into production
            as it contains sensitive information for the development
            environment.

:Example:
    Example code use::

        # Run all tests via the shell script.
        ./run.sh

        # Run all tests using unittest.
        python -m unittest discover

        # Run a single test.
        python -m unittest test_search.py

"""
# pylint: disable=unnecessary-pass
# pylint: disable=wrong-import-position

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import unittest


class TestBase(unittest.TestCase):
    """Private generalised base-testing class.

    This class is designed to be inherited by each test-specific class.

    """

    _DIR_ROOT = os.path.realpath(os.path.dirname(__file__))
    _DIR_RESC = os.path.join(_DIR_ROOT, 'resources')
    _DIR_DATA = os.path.join(_DIR_RESC, 'data')

    @classmethod
    def setUpClass(cls):
        """Setup the testing class once, for all tests."""
        pass

    @classmethod
    def tearDownClass(cls):
        """Teardown the testing class once all tests are complete."""
        pass
