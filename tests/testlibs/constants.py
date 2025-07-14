#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides constants which are dedicated to the
            unit tests.

:Platform:  Linux/Windows | Python 3.6
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

:Example:
    Example code use::

        from testlibs.constants import templates

"""
# pylint: disable=too-few-public-methods


class _StartOfTest:
    """Start of test messages class."""

    @property
    def database_mssql(self):
        """SQL Server database functionality testing start of test message."""
        return 'MS SQL Server database interface'

    @property
    def database_mysql(self):
        """MySQL database functionality testing start of test message."""
        return 'MySQL database interface'

    @property
    def database_sqlite(self):
        """SQLite database functionality testing start of test message."""
        return 'SQLite database interface'


class _Templates:
    """String templates used across the various unit tests."""

    def __init__(self):
        """Private _Templates class initialiser."""
        self._notexp = self._NotAsExpected()

    @property
    def not_as_expected(self):
        """_NotAsExpected testing templates accessor."""
        return self._notexp


    class _NotAsExpected():
        """'Not as expected' templates for the testing classes."""

        @property
        def database(self):
            """'Value not as expected' template for database tests."""
            return ('\n\nThe database test was not as expected.\n'
                    '- Expected: {}\n'
                    '- Actual: {}')


startoftest = _StartOfTest()
templates = _Templates()
