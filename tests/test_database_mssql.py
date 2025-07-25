#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:Purpose:   Testing module for the ``database`` module; specifically
            SQL Server functionality.

:Tests:     Refer to the :class:`~TestDatabaseSQLServer` docstring.

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
from glob import glob
from utils4 import utils
# locals
from base import TestBase
from testlibs.constants import startoftest
from testlibs.constants import templates
from testlibs.utilities import utilities
from dbilib._dbi_base import ExitCode
from dbilib.database import DBInterface


class TestDatabaseMSSQL(TestBase):
    """Testing class used to test the MS SQL Server database interface.

    :Tests Overview:

        For specific testing details, refer to the docstring of each
        testing method. As a whole, the tests cover all methods in the
        ``dbilib.database`` module.

    """
    # pylint: disable=too-many-public-methods

    _MSG1 = templates.not_as_expected.database
    _CREDS = {'database': 'dbilib_test',
              'drivername': 'mssql+pyodbc',
              'host': '<REMOVED>',
              'password': '',
              'port': 50002,
              'username': '',
              'driver': 'ODBC+Driver+17+for+SQL+Server',
              'trusted_connection': 'yes'}
    _CONNSTR_T = ('{drivername}://{username}:{password}@{host}:{port}/{database}'
                  '?driver={driver}'
                  '&trusted_connection={trusted_connection}')
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
        if not utils.testimport('pyodbc'):
            msg = 'Skipping MS SQL Server tests.'
            print(msg)  # Not printed from the raise.
            raise cls().skipTest(msg)
        cls.ignore_warnings()
        utilities.msgs.print_testing_start(msg=startoftest.database_mssql)
        cls._db_teardown()  # Start from scratch.
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
        if utils.testimport('pyodbc'):
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
            if key not in ('driver', 'trusted_connection'):
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

    def test02b__table_exists__not_exist(self):
        """Test the table exists method returns False.

        :Test:
            - Create a database object using the connection string.
            - Verify the ``table_exists`` method returns False for a
              table which does not exist.

        """
        dbi = DBInterface(connstr=self._CONNSTR)
        tst = dbi.table_exists(table_name='some_table', verbose=False)
        self.assertFalse(tst, msg=self._MSG1.format(False, tst))

    def test02c__table_exists__not_exist_w_msg(self):
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

    def test02d__checksum(self):
        """Test the checksum method.

        :Test:
            - Create a database object using the connection string.
            - Verify the ``checksum`` method returns the expected value
              for the initial load of the 'guitars' table.

        Note: This method is named ``test02d_`` as the test must come
              before the 'test03' cases which begin altering the table
              data.

        """
        dbi = DBInterface(connstr=self._CONNSTR)
        exp = -1220601258
        tst = dbi.checksum(table_name='guitars')
        self.assertEqual(exp, tst)

    def test02e__checksum__not_exist(self):
        """Test the checksum method, for a table which does not exist.

        :Test:
            - Create a database object using the connection string.
            - Verify the ``checksum`` method returns the expected value
              for a non-existant table.

        Note: This method is named ``test02d_`` as the test must come
              before the 'test03' cases which begin altering the table
              data.

        """
        dbi = DBInterface(connstr=self._CONNSTR)
        exp = None
        tst = dbi.checksum(table_name='idontexist')
        self.assertEqual(exp, tst)

    def test03a__call_procedure(self):
        """Test the call_procedure method.

        :Test:
            - Call the ``call_procedure`` method and verify the returned
              results are as expected.

        """
        fname = f'{self.id().split(".")[-1]}.p'
        dbi = DBInterface(connstr=self._CONNSTR)
        params={'_colour': 'black'}
        df = dbi.call_procedure(proc='usp_get_guitars_colour', params=params, raw=False)
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
        params = {'_make': 'Taylor', '_model': 'Presentation', '_colour': 'Natural'}
        dbi.call_procedure(proc='usp_insert_guitars_add_new', params=params, return_status=False)
        tst = dbi.execute_query('select colour from guitars where model = \'Presentation\'')[0][0]
        self.assertEqual(exp, tst, msg=self._MSG1.format(exp, tst))

    def test04a__call_procedure_update(self):
        """Test the call_procedure_update method, without a return ID.

        :Test:
            - Update the colour of a guitar for a specific ID.
            - Verify the procedure call returned True.
            - Verify the new colour for the ID.

        """
        dbi = DBInterface(connstr=self._CONNSTR)
        exp1 = True
        exp2 = 'green'
        data = {'_id': 1, '_colour': exp2}
        tst1 = dbi.call_procedure_update(proc='usp_update_guitars_colour', data=data)
        tst2 = dbi.execute_query('select colour from guitars where id = 1')[0][0]
        self.assertEqual(exp1, tst1, msg=self._MSG1.format(exp1, tst1))
        self.assertEqual(exp2, tst2, msg=self._MSG1.format(exp2, tst2))

    def test05a__call_procedure_update__with_row_id(self):
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
        exp1 = ([(16,)], True)
        data = {'_make': 'Fender', '_model': 'Stratocaster', '_colour': 'Various'}
        tst1 = dbi.call_procedure_update(proc='usp_insert_guitars_add_new',
                                         data=data,
                                         return_id=True)
        tst1_id = tst1[0][0][0]
        # Collect the ID of the newly added guitar, from the database.
        tst2 = dbi.execute_query(stmt='select id from guitars where colour = :colour',
                                 params={'colour': 'Various'},
                                 raw=True)[0][0]
        # Add players for the new guitar.
        exp3 = [(1,), (2,), (3,), (4,)]
        tst3 = []
        for name in players:
            data = {'_guitars_id': tst1_id, '_name': name}
            id_ = dbi.call_procedure_update(proc='usp_insert_players_add_new', data=data, return_id=True)
            tst3.append(id_[0][0])
        # Test response when queried by ID.
        tst4 = dbi.execute_query(stmt='select distinct name from players where guitars_id = :id order by name',
                                 params={'id': tst1_id},
                                 raw=True)
        tst4 = [i[0] for i in tst4]
        self.assertEqual(exp1, tst1, msg=self._MSG1.format(exp1, tst1))
        self.assertEqual(tst1_id, tst2, msg=self._MSG1.format(tst1_id, tst2))
        self.assertTrue(exp3, msg=self._MSG1.format(True, tst3))
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
            - Verify the method returned None, for other operations.
            - Call the ``execute_query`` method with a ``DROP TABLE``
              statement which does not return a value.

        """
        dbi = DBInterface(connstr=self._CONNSTR)
        tst1 = dbi.execute_query(stmt='create table [dbo].[foo] ([id] integer);')
        tst2 = dbi.table_exists('foo')
        tst3 = dbi.execute_query(stmt='drop table [dbo].[foo];')
        tst4 = dbi.table_exists('foo')
        self.assertIsNone(tst1)
        self.assertTrue(tst2)
        self.assertIsNone(tst3)
        self.assertFalse(tst4)

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
        self.assertIsNone(tst)

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
        self.assertIsNone(tst)

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
            dbi.call_procedure_update_raw(proc='usp_update_guitars_colour',
                                                data={'_id': 1, '_colour': 'Blue'})
        tst = buff.getvalue()
        self.assertEqual(exp, tst, msg=self._MSG1.format(exp, tst))

    def test07b__call_procedure_update_raw__invalid_usp(self):
        """Test the call_procedure_update_raw method, with an invalid USP.

        :Test:
            - Call the raw procedure (with a non-existant USP) and verify
              the error propogates back through to this test case.

        """
        # pylint: disable=broad-exception-caught  # It's OK.
        buff = io.StringIO()
        exp = 'Could not find stored procedure \'usp_i_dont_exist\'.'
        dbi = DBInterface(connstr=self._CONNSTR)
        with contextlib.redirect_stdout(buff):
            try:
                _ = dbi.call_procedure_update_raw(proc='usp_i_dont_exist', data={})
            except Exception as err:
                print(err)
        tst = buff.getvalue()
        self.assertIn(exp, tst)

    def test08a__database_exists(self):
        """Test the database exists method returns True.

        :Test:
            - Create a database object using the connection string.
            - Verify the ``database_exists`` method returns True for the
              'dbilib_test' and '__bak__dbilib_test' tables.

        """
        dbi = DBInterface(connstr=self._CONNSTR)
        for db in ('dbilib_test', '__bak__dbilib_test'):
            tst = dbi.database_exists(database_name=db, verbose=False)
            self.assertTrue(tst)

    def test08b__database_exists__not_exist(self):
        """Test the database exists method returns False.

        :Test:
            - Create a database object using the connection string.
            - Verify the ``database_exists`` method returns False for a
              database which does not exist.

        """
        dbi = DBInterface(connstr=self._CONNSTR)
        tst = dbi.database_exists(database_name='idontexist', verbose=False)
        self.assertFalse(tst)

    def test08c__database_exists__not_exist_w_msg(self):
        """Test the database exists method returns False, in verbose mode.

        :Test:
            - Create a database object using the connection string.
            - Verify the ``database_exists`` method returns False for a
              database which does not exist.
            - Verify the stdout text is as expected.

        """
        buff = io.StringIO()
        dbi = DBInterface(connstr=self._CONNSTR)
        with contextlib.redirect_stdout(buff):
            tst1 = dbi.database_exists(database_name='idontexist', verbose=True)
        tst2 = buff.getvalue()
        exp1 = False
        exp2 = 'Database does not exist'
        exp3 = 'idontexist'
        self.assertFalse(tst1, msg=self._MSG1.format(exp1, tst1))
        self.assertIn(exp2, tst2, msg=self._MSG1.format(exp2, tst2))
        self.assertIn(exp3, tst2, msg=self._MSG1.format(exp3, tst2))

    def test09a__get_parameter_name__not_exist(self):
        """Test the ``get_parameter_name`` method.

        :Test:
            - Create a database object using the connection string.
            - Verify the ``get_parameter_name`` method returns the
              expected results.

        """
        dbi = DBInterface(connstr=self._CONNSTR)
        exp = ('_id', '_colour')
        tst = dbi.get_parameter_names(proc='usp_update_guitars_colour')
        self.assertEqual(exp, tst)

    def test09b__get_parameter_name__not_exist(self):
        """Test the ``get_parameter_name`` method for a USP which does
        not exist.

        :Test:
            - Create a database object using the connection string.
            - Verify the ``get_parameter_name`` returns the expected
              value.

        """
        dbi = DBInterface(connstr=self._CONNSTR)
        exp = ()
        tst = dbi.get_parameter_names(proc='sp_idontexist')
        self.assertEqual(exp, tst)

    def test10a__backup(self):
        """Test the ``backup`` method.

        :Test:
            - Create a database object using the connection string.
            - Verify the ``backup`` method can backup a table
              successfully.

        """
        buff = io.StringIO()
        dbi = DBInterface(connstr=self._CONNSTR)
        exp1 = ExitCode.OK
        exp2 = 'backup successful'
        with contextlib.redirect_stdout(buff):
            tst1 = dbi.backup(table_name='guitars')
        tst2 = buff.getvalue()
        self.assertEqual(exp1, tst1)
        self.assertIn(exp2, tst2)

    def test10b__backup__verify_checksums(self):
        """Test the ``backup`` method and verify the dataset in each.

        This test is redundant of the previous as the success method for
        determining a successful backup is a checksum test between the
        two tables. However, this case acts as an *explicit* test.

        :Test:
            - Create a database object using the connection string.
            - Verify the ``backup`` method can backup a table
              successfully.
            - Verify the checksums between the source and backup tables
              match.

        """
        buff = io.StringIO()
        dbi = DBInterface(connstr=self._CONNSTR)
        exp1 = ExitCode.OK
        exp2 = 'backup successful'
        with contextlib.redirect_stdout(buff):
            tst1 = dbi.backup(table_name='guitars')
        tst2 = buff.getvalue()
        tst3A = dbi.checksum(table_name='guitars', database_name='dbilib_test')
        tst3B = dbi.checksum(table_name='guitars', database_name='__bak__dbilib_test')
        self.assertEqual(exp1, tst1)
        self.assertIn(exp2, tst2)
        self.assertEqual(tst3A, tst3B)

    def test10c__backup__not_exist(self):
        """Test the ``backup`` method for a table which does not exist.

        :Test:
            - Create a database object using the connection string.
            - Verify the ``backup`` method provides the correct output
              for a table which does not exist.

        """
        buff = io.StringIO()
        dbi = DBInterface(connstr=self._CONNSTR)
        exp1 = ExitCode.ERR_BKUP_TBNEX
        exp2A = 'Table does not exist: dbilib_test.idontexist'
        exp2B = 'backup failed'
        with contextlib.redirect_stdout(buff):
            tst1 = dbi.backup(table_name='idontexist')
        tst2 = buff.getvalue()
        self.assertEqual(exp1, tst1)
        self.assertIn(exp2A, tst2)
        self.assertIn(exp2B, tst2)

# %% Helper methods

    @classmethod
    def _db_setup(cls) -> bool:
        """Run the database setup script, via a subproess.

        Returns:
            bool: True if the setup completes successfully, otherwise
            False.

        """
        dbi = DBInterface(connstr=cls._CONNSTR)
        exp1 = 14  # Expected number of rows to be added.
        tables = glob(os.path.join(cls._DIR_SETUP_MSSQL, 'create', 'create_table__*.sql'))
        usps = glob(os.path.join(cls._DIR_SETUP_MSSQL, 'create', 'create_proc__*.sql'))
        views = glob(os.path.join(cls._DIR_SETUP_MSSQL, 'create', 'create_view__*.sql'))
        for table in tables:
            with open(table, 'r', encoding='utf-8') as f:
                stmt = f.read()
                dbi.execute_query(stmt=stmt)
        for usp in usps:
            with open(usp, 'r', encoding='utf-8') as f:
                stmt = f.read()
                dbi.execute_query(stmt=stmt, ignore_unsafe=True)
        for view in views:
            with open(view, 'r', encoding='utf-8') as f:
                stmt = f.read()
                dbi.execute_query(stmt=stmt)
        df = pd.read_csv(os.path.join(cls._DIR_RAW_DATA_MSSQL, 'data__guitars.csv'))
        rows = df.iloc[:,1:].to_sql('guitars', con=dbi.engine, index=False, if_exists='append')
        return all((
                    all((dbi.table_exists('guitars'), dbi.table_exists('players'))),
                    (exp1 == rows),
                   ))

    @classmethod
    def _db_teardown(cls) -> bool:
        """Run the database deconstruct script, via a subprocess.

        Returns:
            bool: True if the teardown completes successfully, otherwise
            False.

        """
        dbi = DBInterface(connstr=cls._CONNSTR)
        path = os.path.join(cls._DIR_SETUP_MSSQL, 'drop', 'drop__all.sql')
        with open(path, 'r', encoding='utf-8') as f:
            stmt = f.read()
        dbi.execute_query(stmt, ignore_unsafe=True)
        tst1 = dbi.table_exists('guitars')
        tst2 = dbi.table_exists('players')
        return all((tst1 is False, tst2 is False))
