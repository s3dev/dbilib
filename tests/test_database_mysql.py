#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:Purpose:   Testing module for the ``database`` module; specifically
            MySQL functionality.

:Tests:     Refer to the :class:`~TestDatabaseMySQL` docstring.

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
from mysql.connector.errors import ProgrammingError
from utils4 import utils
# locals
from base import TestBase
from testlibs.constants import startoftest
from testlibs.constants import templates
from testlibs.utilities import utilities
from dbilib.database import DBInterface



class TestDatabaseMySQL(TestBase):
    """Testing class used to test the MySQL database interface.

    :Tests Overview:

        For specific testing details, refer to the docstring of each
        testing method. As a whole, the tests cover all methods in the
        ``dbilib.database`` module.

    """

    _MSG1 = templates.not_as_expected.database
    _CREDS = {'database': 'dbilib_test',
              'drivername': 'mysql+mysqlconnector',
              'host': 'localhost',
              'password': 'testing123',
              'port': 3306,
              'username': 'testuser'}
    _CONNSTR_T = '{drivername}://{username}:{password}@{host}:{port}/{database}'
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
        cls.ignore_warnings()
        utilities.msgs.print_testing_start(msg=startoftest.database_mysql)
        if not cls._db_setup():
            msg = 'The database setup failed. All further module testing aborted.'
            print(msg)  # Not printed from the raise.
            cls._db_teardown()
            raise cls().skipTest(msg)

    @classmethod
    def tearDownClass(cls):
        """Actions to be performed once all tests are complete.

        :Actions:
            - Deconstruct the testing database.

        """
        cls._db_teardown()

    def test01a__engine(self):
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

    def test01b__database_name(self):
        """Test the database name property.

        :Test:
            - Verify the database name (as parsed from the ``engine``
              object) is as expected.

        """
        dbi = DBInterface(connstr=self._CONNSTR)
        tst = dbi.database_name
        exp = dbi.engine.url.database
        self.assertEqual(exp, tst, msg=self._MSG1.format(exp, tst))

    def test02a__table_exists(self):
        """Test the table exists method returns True.

        :Test:
            - Create a database object using the connection string.
            - Verify the ``table_exists`` method returns True for the
              'guitars' table.

        """
        dbi = DBInterface(connstr=self._CONNSTR)
        tst = dbi.table_exists(table_name='guitars', verbose=False)
        self.assertTrue(tst, msg=self._MSG1.format(True, tst))

    def test02b__table_exists(self):
        """Test the table exists method returns False.

        :Test:
            - Create a database object using the connection string.
            - Verify the ``table_exists`` method returns False for a
              table which does not exist.

        """
        dbi = DBInterface(connstr=self._CONNSTR)
        tst = dbi.table_exists(table_name='some_table', verbose=False)
        self.assertFalse(tst, msg=self._MSG1.format(False, tst))

    def test02c__table_exists(self):
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
        exp3 = 'dbilib_test.some_table'
        self.assertFalse(tst1, msg=self._MSG1.format(exp1, tst1))
        self.assertIn(exp2, tst2, msg=self._MSG1.format(exp2, tst2))
        self.assertIn(exp3, tst2, msg=self._MSG1.format(exp3, tst2))

    def test03a__call_procedure(self):
        """Test the call_procedure method.

        :Test:
            - Call the ``call_procedure`` method and verify the returned
              results are as expected.

        """
        fname = f'{self.id().split(".")[-1]}.p'
        dbi = DBInterface(connstr=self._CONNSTR)
        df = dbi.call_procedure(proc='sp_get_guitars_colour', params=['black'])
        exp = pd.read_pickle(os.path.join(self._DIR_DATA, fname))
        self.assertTrue(exp.equals(df.iloc[:,1:]), msg=self._MSG1.format(exp, df))

    def test03b__call_procedure__insert(self):
        """Test the call_procedure method for an INSERT USP.

        This test case is designed to test the method's ``conn.commit()``
        call inserts and commits the new data.

        :Test:
            - Call the ``call_procedure`` method to insert new data.
            - Query the table to verify the returned results are as
              expected.

        """
        dbi = DBInterface(connstr=self._CONNSTR)
        exp = 'Natural'
        params = ('Taylor', 'Presentation', 'Natural')
        _ = dbi.call_procedure(proc='sp_insert_guitars_add_new', params=params, return_status=False)
        tst = dbi.execute_query('select colour from guitars where model = \'Presentation\'')[0][0]
        self.assertEqual(exp, tst, msg=self._MSG1.format(exp, tst))

    def test04__call_procedure_update(self):
        """Test the call_procedure_update method, without a return ID.

        :Test:
            - Update the colour of a guitar for a specific ID.
            - Verify the procedure call returned True.
            - Verify the new colour for the ID.

        """
        dbi = DBInterface(connstr=self._CONNSTR)
        exp1 = True
        exp2 = 'green'
        tst1 = dbi.call_procedure_update(proc='sp_update_guitars_colour', params=[1, exp2])
        tst2 = dbi.execute_query('select colour from guitars where id = 1')[0][0]
        self.assertEqual(exp1, tst1, msg=self._MSG1.format(exp1, tst1))
        self.assertEqual(exp2, tst2, msg=self._MSG1.format(exp2, tst2))

    def test05__call_procedure_update__with_row_id(self):
        """Test the call_procedure_update method, with a return ID.

        :Test:
            - Call the ``call_procedure_update`` method to add a new
              guitar, with the ``return_id`` argument set to True.
            - Call the ``execute_query`` method to obtain the newly
              added ID directly from the database (for testing).
            - Call the ``call_procedure_update_many`` method to add new
              players for the newly added guitar, passing in the ID
              returned from the previous method.
            - Call the ``execute_query`` method to collect the names of
              the players just added, matching the ``guitars_id`` of the
              newly added guitar.
            - Verify the first procedure call (adding the new guitar)
              returned the expected  results.
            - Verify the ID returned by the first procedure call matches
              that of the one actually assigned by the database.
            - Verify the second procedure call (adding the new players)
              returned the expected results.
            - Verify the players added to the database are as expected.

        """
        # pylint: disable=line-too-long
        players  = ['David Gilmour', 'Eric Clapton', 'Eric Johnson', 'Mark Knopfler']
        dbi = DBInterface(connstr=self._CONNSTR)
        # Add new guitar.
        exp1 = (16, True)
        tst1 = dbi.call_procedure_update(proc='sp_insert_guitars_add_new',
                                         params=['Fender', 'Stratocaster', 'Various'],
                                         return_id=True)
        # Collect the ID of the newly added guitar, from the database.
        tst2 = dbi.execute_query(stmt='select id from guitars where colour = :colour',
                                 params={'colour': 'Various'},
                                 raw=True)[0][0]
        # Add players for the new guitar.
        tst3 = dbi.call_procedure_update_many(tst1[0],
                                              proc='sp_insert_players_add_new',
                                              iterable=players)
        tst4 = dbi.execute_query(stmt='select name from players where guitars_id = :id order by name',
                                 params={'id': tst1[0]},
                                 raw=True)
        tst4 = [i[0] for i in tst4]
        self.assertEqual(exp1, tst1, msg=self._MSG1.format(exp1, tst1))
        self.assertEqual(exp1[0], tst2, msg=self._MSG1.format(exp1[0], tst2))
        self.assertTrue(tst3, msg=self._MSG1.format(True, tst3))
        self.assertEqual(players, tst4, msg=self._MSG1.format(players, tst4))

    def test06a__execute_query__raw(self):
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

    def test06b__execute_query__dataframe(self):
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

    def test06c__execute_query__none(self):
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

    def test06d__execute_query__security01(self):
        """Test the execute_query method with multiple semi-colon statement.

        The statement used in this query was tested in its 'before' and
        'after' state, and is a valid injection-like statement.

        :Test:
            - Call the ``execute_query`` method with a statement
              containing multiple semi-colons - simulating an injection
              attack.
            - Verify a SecurityWarning is raised and nothing is
              returned.

        """
        buff = io.StringIO()
        dbi = DBInterface(connstr=self._CONNSTR)
        stmt = "select * from guitars where colour = '{}'"
        stmt_ = stmt.format("green'; delete from guitars; --")
        with contextlib.redirect_stdout(buff):
            tst = dbi.execute_query(stmt=stmt_)
        self.assertIn('SecurityWarning: Multiple statements', buff.getvalue())
        self.assertIs(None, tst, msg=self._MSG1.format(None, tst))

    def test06e__execute_query__security02(self):
        """Test the execute_query method with a comment string.

        The statement used in this query was tested in its 'before' and
        'after' state, and is a valid injection-like statement.

        :Test:
            - Call the ``execute_query`` method with a statement
              containing a comment - simulating an injection attack.
            - Verify a SecurityWarning is raised and nothing is
              returned.

        """
        buff = io.StringIO()
        dbi = DBInterface(connstr=self._CONNSTR)
        stmt = "select * from guitars where colour = '{}'"
        stmt_ = stmt.format("green'; --")
        with contextlib.redirect_stdout(buff):
            tst = dbi.execute_query(stmt=stmt_)
        self.assertIn('SecurityWarning: Comments are not allowed', buff.getvalue())
        self.assertIs(None, tst, msg=self._MSG1.format(None, tst))

    def test07a__call_procedure_update_raw__no_error(self):
        """Test the call_procedure_update_raw method, no errors.

        :Test:
            - Call the raw procedure (without generating an error) and
              verify the returned value is None.

        """
        buff = io.StringIO()
        dbi = DBInterface(connstr=self._CONNSTR)
        exp = ''
        with contextlib.redirect_stdout(buff):
            dbi.call_procedure_update_raw(proc='sp_update_guitars_colour',
                                                params=[1, 'blue'])
        tst = buff.getvalue()
        self.assertEqual(exp, tst, msg=self._MSG1.format(exp, tst))

    def test07b__call_procedure_update_raw__invalid_usp(self):
        """Test the call_procedure_update_raw method, with an invalid USP.

        :Test:
            - Call the raw procedure (with a non-existant USP) and verify
              the error is trapped locally.

        """
        buff = io.StringIO()
        exp = '1305 (42000): PROCEDURE dbilib_test.sp_i_dont_exist does not exist\n'
        dbi = DBInterface(connstr=self._CONNSTR)
        with contextlib.redirect_stdout(buff):
            try:
                dbi.call_procedure_update_raw(proc='sp_i_dont_exist', params=[])
            except ProgrammingError as err:
                print(err)
        tst = buff.getvalue()
        self.assertEqual(exp, tst, msg=self._MSG1.format(exp, tst))

    def test08__database_not_supported(self):
        """Test the error raised by providing a non-supported database.

        Note: The ``pyodbc`` library must be installed for this test.

        :Test:
            - Using a valid connection string for a database which is
              not currently supported, create an instance of the
              ``DBInterface`` class, and test for a
              ``NotImplementedError`` to be raised, listing the
              supported databases.

        """
        if utils.testimport('pyodbc'):
            with self.assertRaises(NotImplementedError):
                DBInterface(connstr='mssql+pyodbc://user:pwd@localhost/spam')

    @classmethod
    def _db_setup(cls) -> bool:
        """Run the database setup script, via a subproess.

        Returns:
            bool: True if the setup completes successfully, otherwise
            False.

        """
        args = ['resources/db_setup_mysql.sh', cls._CREDS.get('password')]
        p_data = os.path.join(cls._DIR_RAW_DATA_MYSQL, 'data__guitars.csv')
        with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
            _ = proc.communicate()
        # Invert the bit so exit code 0 is True, and visa versa.
        if proc.returncode ^ 1:
            dbi = DBInterface(connstr=cls._CONNSTR)
            pd.read_csv(p_data).to_sql('guitars', con=dbi.engine, index=False, if_exists='append')
            # Count records added.
            rtn = pd.read_sql('select count(*) from guitars', con=dbi.engine).to_records()
            # Count expected records.
            with open(p_data, encoding='utf-8') as f:
                exp_rows = len(f.readlines()) - 1  # Subtract the header.
            # Verify the expected number of values were loaded.
            if rtn[0][1] == exp_rows:
                return True
        return False

    @classmethod
    def _db_teardown(cls) -> bool:
        """Run the database deconstruct script, via a subprocess.

        Returns:
            bool: True if the teardown completes successfully, otherwise
            False.

        """
        # args = ['resources/db_teardown_mysql.sh', self._CREDS.get('password')]
        args = ['resources/db_teardown_mysql.sh', cls._CREDS.get('password')]
        with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
            _ = proc.communicate()
        # Invert the bit so exit code 0 is True, and visa versa.
        return proc.returncode ^ 1
