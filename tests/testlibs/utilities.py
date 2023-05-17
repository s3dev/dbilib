#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides shared utilities, which are dedicated
            to unit testing.

:Platform:  Linux/Windows | Python 3.6
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

:Example:
    Example code use::

        from testlibs.utilities import utilities

"""
# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods

from time import sleep


class _Utilities:
    """Shared utilities used exclusively for unit testing."""

    def __init__(self):
        """Unit testing utilities class initialiser."""
        self._msgs = self._Messages()

    @property
    def msgs(self):
        """Messages class accessor."""
        return self._msgs


    class _Messages:
        """General testing messages utility class."""

        @staticmethod
        def print_testing_start(msg):
            """Print a start of testing message.

            Args:
                msg (str): Short description for this section of tests.

            """
            n = 70
            print('\n\n', '-' * n, sep='')
            print(f'***   Starting test for: {msg}   ***'.center(n))
            print('-' * n, '\n', sep='')
            sleep(0.25)


utilities = _Utilities()
