#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:Purpose:   Testing module for the ``database`` module; specifically
            SQLite functionality.

:Tests:     Refer to the :class:`~TestDatabaseSQLite` docstring.

:Platform:  Linux/Windows | Python 3.6+
:Developer: J Berendt
:Email:     development@s3dev.uk

:Comments:  n/a

"""
# pylint: disable=import-error
# pylint: disable=invalid-name
# pylint: disable=wrong-import-order

import contextlib
import io
import os
import pandas as pd
import subprocess
# locals
from base import TestBase
from testlibs.constants import startoftest
from testlibs.constants import templates
from testlibs.utilities import utilities
from dbilib.database import DBInterface


class TestDatabaseSQLite(TestBase):
    """Testing class used to test the SQLite database interface.

    :Tests Overview:

        For specific testing details, refer to the docstring of each
        testing method. As a whole, the tests cover all methods in the
        ``dbilib.database`` module.

    """

    _MSG1 = templates.not_as_expected.database
    _CREDS = {'drivername': 'sqlite',
              'database': os.path.join(TestBase._DIR_RESC, 'testdatabase.db')}
    _CONNSTR_T = '{drivername}:///{database}'
    _CONNSTR = _CONNSTR_T.format(**_CREDS)

    @classmethod
    def setUpClass(cls):
        """Actions to be performed at the start of testing.

        :Tasks:
            - Print the start of testing message.
            - Run the database setup script. If the setup completes
              successfully, testing proceeds. If the setup fails, all
              testing is aborted.

        """
        utilities.msgs.print_testing_start(msg=startoftest.database_sqlite)
        if not cls._db_setup():
            msg = 'The database setup failed. All further module testing aborted.'
            print(msg)  # Not printed from the raise.
            raise cls().skipTest(msg)

    @classmethod
    def tearDownClass(cls):
        """Actions to be performed once all tests are complete.

        :Actions:
            - Delete the testing database file.

        """
        cls._db_teardown()

    def test01__engine(self):
        """Test the engine object created by ``sqlalchemy``.

        :Test:
            - Iterate through the database credentials supplied to create
              the ``engine`` object, and verify the created ``engine``
              contains the identical values from the credentials.

        """
        #pylint: disable=unnecessary-dunder-call
        dbi = DBInterface(connstr=self._CONNSTR)
        for key, val in self._CREDS.items():
            with self.subTest(msg=f'{key=}, {val=}'):
                tst = dbi.engine.url.__getattribute__(key)
                self.assertEqual(val, tst, msg=self._MSG1.format(val, tst))

    def test02__file_not_found(self):
        """Test the interface creation for a non-exist database file.

        :Test:
            - Verify a FileNotFoundError is raised when a database file
              is passed which does not exist.

        """
        with self.assertRaises(FileNotFoundError):
            DBInterface(connstr='sqlite:////tmp/notexist.db')

    def test03a__table_exists(self):
        """Test the table exists method returns True.

        :Test:
            - Create a database object using the connection string.
            - Verify the ``table_exists`` method returns True for the
              'guitars' table.

        """
        dbi = DBInterface(connstr=self._CONNSTR)
        tst = dbi.table_exists(table_name='guitars', verbose=False)
        self.assertTrue(tst, msg=self._MSG1.format(True, tst))

    def test03b__table_exists(self):
        """Test the table exists method returns False.

        :Test:
            - Create a database object using the connection string.
            - Verify the ``table_exists`` method returns False for a
              table which does not exist.

        """
        dbi = DBInterface(connstr=self._CONNSTR)
        tst = dbi.table_exists(table_name='some_table', verbose=False)
        self.assertFalse(tst, msg=self._MSG1.format(False, tst))

    def test03c__table_exists(self):
        """Test the table exists method returns False, in verbose mode.

        :Test:
            - Create a database object using the connection string.
            - Verify the ``table_exists`` method returns False for a
              table which does not exist.
            - Verify the stdout text is as expected.

        """
        buff = io.StringIO()
        dbi = DBInterface(connstr=self._CONNSTR)
        with contextlib.redirect_stdout(buff):
            tst1 = dbi.table_exists(table_name='some_table', verbose=True)
        tst2 = buff.getvalue()
        exp1 = False
        exp2 = 'Table does not exist'
        exp3 = f'{self._CREDS.get("database")}.some_table'
        self.assertFalse(tst1, msg=self._MSG1.format(exp1, tst1))
        self.assertIn(exp2, tst2, msg=self._MSG1.format(exp2, tst2))
        self.assertIn(exp3, tst2, msg=self._MSG1.format(exp3, tst2))

    def test04a__execute_query__raw(self):
        """Test the execute_query method, returning raw results.

        :Test:
            - Call the ``execute_query`` method with a parameter.
            - Verify the results are as expected.

        """
        dbi = DBInterface(connstr=self._CONNSTR)
        exp = [(3,)]
        tst = dbi.execute_query(stmt='select count(*) from guitars where colour = :colour',
                                params={'colour': 'Black'},
                                raw=True)
        self.assertEqual(exp, tst, msg=self._MSG1.format(exp, tst))

    def test04b__execute_query__dataframe(self):
        """Test the execute_query method, returning a DataFrame.

        :Test:
            - Call the ``execute_query`` method with a parameter.
            - Verify the results are as expected.

        """
        dbi = DBInterface(connstr=self._CONNSTR)
        exp = pd.DataFrame({'c': 3}, index=[0])
        tst = dbi.execute_query(stmt='select count(*) as c from guitars where colour = :colour',
                                params={'colour': 'Black'},
                                raw=False)
        self.assertTrue(exp.equals(tst), msg=self._MSG1.format(exp, tst))

    def test04c__execute_query__none(self):
        """Test the execute_query method, returning None.

        :Test:
            - Call the ``execute_query`` method with a ``CREATE TABLE``
              statement which does not return a value.
            - Call the method again with a ``DROP TABLE`` statement to
              cleanup.
            - Verify the method returned None, for other operations.

        """
        dbi = DBInterface(connstr=self._CONNSTR)
        exp = None
        tst1 = dbi.execute_query(stmt='create table foo (id integer)')
        tst2 = dbi.execute_query(stmt='drop table foo')
        self.assertTrue(all([tst1 is None, tst2 is None]),
                        msg=self._MSG1.format(exp, (tst1, tst2)))

    @classmethod
    def _db_setup(cls) -> bool:
        """Run the database setup script, via a subproess.

        Returns:
            bool: True if the setup completes successfully, otherwise
            False.

        """
        args = ['resources/db_setup_sqlite.sh', cls._CREDS.get('database')]
        with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
            _ = proc.communicate()
        # Invert the bit so exit code 0 is True, and visa versa.
        if proc.returncode ^ 1:
            dbi = DBInterface(connstr=cls._CONNSTR)
            rtn = (pd.read_csv(os.path.join(cls._DIR_RAW_DATA_SQLITE, 'data__guitars.csv'))
                   .to_sql('guitars', con=dbi.engine, index=False, if_exists='append'))
            # Verify the expected number of values were loaded.
            if rtn == 14:
                return True
        return False

    @classmethod
    def _db_teardown(cls) -> bool:
        """Run the database deconstruct script, via a subprocess.

        Returns:
            bool: True if the teardown completes successfully, otherwise
            False.

        """
        args = ['resources/db_teardown_sqlite.sh', cls._CREDS.get('database')]
        with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
            _ = proc.communicate()
        # Invert the bit so exit code 0 is True, and visa versa.
        return proc.returncode ^ 1
