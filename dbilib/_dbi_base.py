#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module contains the library's *base* database methods
            and attribute accessors, which are designed to be
            specialised by the database-specific modules and classes.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     support@s3dev.uk

:Comments:  This module contains *only* methods which can safely be
            inherited and used by *any* of its subclasses.

            In other words, this module should *not* contain any import
            statement, or uses of these imports, which if used in a
            database-specific module will cause a crash due to a missing
            library.

            Any database-specific functionality must be contained in
            that module.

:Example:

    For class-specific usage examples, please refer to the docstring
    for the following classes:

        - :class:`_DBIBase`

"""
# pylint: disable=wrong-import-order

import pandas as pd
import traceback
import sqlalchemy as sa
from sqlalchemy.exc import SQLAlchemyError
from utils4.reporterror import reporterror
from utils4.user_interface import ui


class SecurityWarning(Warning):
    """Security warning stub-class."""


class _DBIBase:
    """This class holds the methods and properties which are used across
    all databases. Each of the database-specific constructors inherits
    this class for its members.

    Note:
        This class is *not* designed to be interacted with directly.

        Rather, please use the :class:`database.DBInterface` class
        instead, as the proper interface class has an automatic switch
        for database interfaces, based on the ``sqlalchemy.Engine``
        object which is created from the connection string.

    Args:
        connstr (str): The database-specific SQLAlchemy connection
            string.

    :Example Use:

        This low-level generalised class is designed to be inherited by
        the calling/wrapping class as::

            >>> from dbilib.database import DBInterface

            class MyDB(DBInterface):

                def __init__(self, connstr: str):
                    super().__init__(connstr=('mysql+mysqlconnector://'
                                              '<user>:<pwd>@<host>:<port>/'
                                              '<db_name>'))

    """

    _PREFIX = '\n[DatabaseError]:'

    def __init__(self, connstr: str):
        """Class initialiser."""
        self._connstr = connstr
        self._engine = None
        if connstr:
            # Testing: Enable an instance to be created without a
            # connection string.
            self._engine = self._create_engine()

    @property
    def database_name(self):
        """Accessor to the database name used by the :attr:`engine` object."""
        return self._engine.url.database

    @property
    def engine(self):
        """Accessor to the ``sqlalchemy.engine.base.Engine`` object."""
        return self._engine

    def execute_query(self,
                      stmt: str,
                      params: dict=None,
                      raw: bool=True) -> list | pd.DataFrame | None:
        """Execute a query statement.

        Important:
            The following are *not* allowed to be executed by this
            method:

                - Statements containing multiple semi-colons (``;``).
                - Statements containing a comment delimiter (``--``).

            If found, a :class:`SecurityWarning` will be raised by the
            :meth:`_is_dangerous` method.

        Args:
            stmt (str): Statement to be executed. The parameter bindings
                are to be written in colon format.
            params (dict, optional): Parameter key/value bindings as a
                dictionary, if applicable. Defaults to None.
            raw (bool, optional): Return the data in 'raw' (tuple)
                format rather than as a formatted DataFrame.
                Defaults to True for efficiency.

        If the query did not return results and the ``raw`` argument is
        False, an empty DataFrame containing the column names only, is
        returned.

        Note:
            In the SQL query, the bind parameters are specified by name,
            using the format ``:bind_name``. The ``params`` dictionary
            argument must contain the associated parameter name/value
            bindings.

        Warning:

            1) Generally, whatever statement is passed into this method
               **will be executed**, and may have *destructive
               implications.*

            2) This method contains a ``commit`` call.

            If a statement is passed into this method, and the user has
            the appropriate permissions - the change
            **will be committed**.

            **... HC SVNT DRACONES.**

        Returns:
            list | pd.DataFrame | None: If the ``raw`` parameter is
            True, a list of tuples containing values is returned.
            Otherwise, a ``pandas.DataFrame`` object containing the
            returned data is returned.

            If this method is called with a script which does not return
            results, for example a CREATE script, None is returned;
            regardless of the value passed to the ``raw`` parameter.

        """
        # Additional else and return used for clarity.
        # pylint: disable=no-else-return
        # The error does have a _message member.
        # pylint: disable=no-member
        try:
            # Perform a cursory 'security check.'
            if not self._is_dangerous(stmt=stmt):
                with self._engine.connect() as conn:
                    result = conn.execute(sa.text(stmt), params)
                    conn.commit()
                    conn.close()
                if raw:
                    return result.fetchall()
                else:
                    return self._result_to_df__cursor(result=result)
        except SecurityWarning:
            print(traceback.format_exc())
        except Exception as err:
            if 'object does not return rows' not in err._message():
                reporterror(err)
        return None

    def _create_engine(self) -> sa.engine.base.Engine:
        """Create a database engine using the provided environment.

        Returns:
            sqlalchemy.engine.base.Engine: A sqlalchemy database engine
            object.

        """
        # ???: Do these values need to be moved to an external config?
        # Added in s3ddb v0.7.0:
        # The pool_* arguments to prevent MySQL timeout which causes
        # a broken pipe and lost connection errors.
        return sa.create_engine(url=self._connstr,
                                poolclass=sa.pool.QueuePool,
                                pool_size=20,
                                pool_recycle=3600,
                                pool_timeout=30,
                                pool_pre_ping=True,
                                max_overflow=0)

    @staticmethod
    def _is_dangerous(stmt: str) -> bool:
        """Perform a dirty security check for injection attempts.

        Args:
            stmt (str): SQL statement to be potentially executed.

        Raises:
            SecurityWarning: If there are multiple semi-colons (``;``)
                in the statement, or any comment delimiters (``--``).

        Returns:
            bool: False if the checks pass.

        """
        # import sys
        if stmt.count(';') > 1:
            msg = 'Multiple statements are disallowed for security reasons.'
            raise SecurityWarning(msg)
            # sys.exit(1)
        if '--' in stmt:
            msg = 'Comments are not allowed in the statement for security reasons.'
            raise SecurityWarning(msg)
        return False

    def _report_sa_error(self, msg: str, error: SQLAlchemyError):  # pragma: nocover
        """Report SQLAlchemy error to the terminal.

        Args:
            msg (str): Additional error to be displayed. This message
                will be automatically prefixed with '[DatabaseError]: '
            error (sqlalchemy.exc.SQLAlchemyError): Caught error object
                from the try/except block.

        """
        msg = f'\n{self._PREFIX} {msg}'
        stmt = f'- Statement: {error.statement}'
        errr = f'- Error: {str(error.orig)}'
        ui.print_alert(text=msg)
        ui.print_alert(text=stmt)
        ui.print_alert(text=errr)

    @staticmethod
    def _result_to_df__cursor(result: sa.engine.cursor.CursorResult) -> pd.DataFrame:
        """Convert a ``CursorResult`` object to a DataFrame.

        If the cursor did not return results, an empty DataFrame
        containing the column names only, is returned.

        Args:
            result (sqlalchemy.engine.cursor.CursorResult): Object to
                be converted.

        Returns:
            pd.DataFrame: A ``pandas.DataFrame`` object containing the
            cursor's data.

        """
        return pd.DataFrame(result, columns=result.keys())

    @staticmethod
    def _result_to_df__stored(result: object) -> pd.DataFrame:
        """Convert a ``MySQLCursor.stored_results`` object to a DataFrame.

        Args:
            result (object): The ``cursor.stored_results()`` object from
            a ``sqlalchemy`` or ``mysql.connector`` procedure call.

        Returns:
            pd.DataFrame: A DataFrame containing the results from the
            procedure call.

        """
        df = pd.DataFrame()
        try:
            # There is only one item in the iterable.
            # However, if the iterable is empty, a StopIteration error is raised
            # when using x = next(result); so a loop is used instead.
            for x in result:
                df = pd.DataFrame(data=x.fetchall(), columns=x.column_names)
        except Exception as err:
            reporterror(err)
        return df
