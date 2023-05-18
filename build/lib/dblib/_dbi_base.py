#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module contains the library's *base* database methods
            and attribute accessors, which are designed to be specialised
            by the database-specific modules and classes.

:Platform:  Linux/Windows | Python 3.6+
:Developer: J Berendt
:Email:     support@s3dev.uk

:Comments:  It's worth noting that this module's core functionality was
            written for MySQL databases. Therefore the MySQL-specific
            database class will modify this base class very little, if
            at all.

            However, there will be more specialisation with regard to
            the Oracle specific classes, as well as MS-SQL when
            implemented.

:Example:

    For class-specific useage examples, please refer to the docstring
    for the following classes:

        - :class:`_DBIBase`

"""
# pylint: disable=wrong-import-order

import pandas as pd
import sqlalchemy as sa
import warnings
from mysql.connector.errors import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from typing import Union, Tuple
from utils4.reporterror import reporterror
from utils4.user_interface import ui


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

            >>> from dblib.database import DBInterface

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
    def engine(self):
        """Accessor to the ``sqlalchemy.engine.base.Engine`` object."""
        return self._engine

    def call_procedure(self,
                       proc: str,
                       params: Union[list, tuple]=None,
                       return_status: bool=False) -> Union[pd.DataFrame,
                                                           Tuple[pd.DataFrame, bool]]:
        """Call a stored procedure, and return as a DataFrame.

        Args:
            proc (str): Name of the stored procedure to call.
            params (Union[list, tuple], optional): A list (or tuple) of
                parameters to pass into the procedure. Defaults to None.
            return_status (bool, optional): Return the method's success
                status. Defaults to False.

        Returns:
            Union[pd.DataFrame, Tuple[pd.DataFrame, bool]]:
            If the ``return_status`` argument is True, a tuple of the
            data and the method's return status is returned as::

                (df, status)

            Otherwise, only the data is returned, as a pd.DataFrame.

        """
        warnings.simplefilter('ignore')
        df = pd.DataFrame()
        success = False
        try:
            # Added in s3ddb v0.7.0.dev1:
            # Updated to use a context manager in an attempt to
            # alleviate the '2055 Lost Connection' and
            # System Error 32 BrokenPipeError.
            with self.engine.connect() as conn:
                cur = conn.connection.cursor(buffered=True)
                cur.callproc(proc, params)
                result = cur.stored_results()
                cur.close()
            df = self._result_to_df__stored(result=result)
            success = not df.empty
        except SQLAlchemyError as err:
            msg = f'Error occurred while running the USP: {proc}.'
            self._report_sqla_error(msg=msg, error=err)
        except Exception as err:
            reporterror(error=err)
        return (df, success) if return_status else df

    def call_procedure_update(self,
                              proc: str,
                              params: list=None,
                              return_id: bool=False) -> Union[bool, tuple]:
        """Call an *update* or *insert* stored procedure.

        Note:
            Results are *not* returned from this call, only a boolean
            status flag and the optional last row ID.

            If results are desired, please use the
            :meth:~`call_procedure` method.

        Args:
            proc_name (str): Name of the stored procedure to call.
            params (list, optional): A list of parameters to pass into
                the USP. Defaults to None.
            return_id (bool, optional): Return the ID of the last
                inserted row. Defaults to False.

        Returns:
            Union[bool, tuple]: If ``return_id`` is False, True is
            returned if the procedure completed  successfully, otherwise
            False. If ``return_id`` is True, a tuple containing the
            ID of the last inserted row and the execution success flag
            are returned as::

                (id, success_flag)

        """
        try:
            rowid = None
            success = False
            # Added in s3ddb v0.7.0.dev1:
            # Updated to use a context manager in an attempt to
            # alleviate the '2055 Lost Connection' and
            # System Error 32 BrokenPipeError.
            with self.engine.connect() as conn:
                cur = conn.connection.cursor()
                cur.callproc(proc, params)
                conn.connection.connection.commit()
                if return_id:
                    # The cur.lastrowid is zero as the mysql_insert_id()
                    # function call applied to a CALL and not the statement
                    # within the procedure. Therefore, it must be manually
                    # obtained here:
                    cur.execute('SELECT LAST_INSERT_ID()')
                    rowid = cur.fetchone()[0]
                cur.close()
                success = True
        except IntegrityError as ierr:
            # Duplicate entry: errno = 1062
            msg = f'{self._PREFIX} {ierr}'
            ui.print_alert(text=msg)
        except Exception as err:
            reporterror(err)
        return (rowid, success) if return_id else success

    def call_procedure_update_many(self, *args, proc: str, iterable: Union[list, tuple]) -> bool:
        """Call an *update* or *insert* stored procedure for an iterable.

        Note:
            The arguments are passed into the USP in the following order:

                *args, iterable_item

            Ensure the USP is designed to accept the iterable item as
            the *last* parameter.

        Args:
            *args (Union[str, int, float]): Positional arguments to be
                passed into the USP, in front of each iterable item.
                Note: The parameters are passed into the USP in the
                order received, followed by the iterable item.
            proc_name (str): Name of the stored procedure to call.
            iterable (Union[list, tuple]): List of items to be loaded
                into the database.

        Returns:
            bool: True if the update was successful, otherwise False.

        """
        try:
            success = False
            with self.engine.connect() as conn:
                cur = conn.connection.cursor()
                for i in iterable:
                    cur.callproc(proc, [*args, i])
                    conn.connection.connection.commit()
                cur.close()
                success = True
        except Exception as err:
            reporterror(err)
        return success

    def call_procedure_update_raw(self, proc: str, params: list=None):
        """Call an *update* or *insert* stored procedure, without error
        handling.

        .. warning::
            This method is **unprotected**, perhaps use
            :meth:`~call_procedure_update` instead.

            This 'raw' method *does not* contain an error handler. It is
            (by design) the responsibility of the caller to contain and
            control the errors.

        The purpose of this raw method is to enable the caller method to
        contain and control the errors which might be generated from a
        USP call, for example a **duplicate key** error.

        Args:
            proc_name (str): Name of the stored procedure to call.
            params (list, optional): A list of parameters to pass into
                the USP. Defaults to None.

        """
        with self._engine.connect() as conn:
            cur = conn.connection.cursor(buffered=True)
            cur.callproc(proc, params)
            conn.connection.connection.commit()
            cur.close()

    def execute_query(self,
                      stmt: str,
                      params: dict=None,
                      raw: bool=True) -> Union[list, pd.DataFrame, None]:
        """Execute a query statement.

        If the query did not return results and the ``raw`` argument is
        False, an empty DataFrame containing the column names only, is
        returned.

        Args:
            stmt (str): Statement to be executed. The parameter bindings
                are to be written in colon format.
            params (dict, optional): Parameter key/value bindings as a
                dictionary, if applicable. Defaults to None.
            raw (bool, optional): Return the data in 'raw' (tuple) format
                rather than as a formatted DataFrame. Defaults to True
                for efficiency.

        Note:
            In the SQL query, the bind parameters are specified by name,
            using the format ``:bind_name``. The ``params`` dictionary
            argument must contain the associated parameter name/value
            bindings.

        Returns:
            Union[list, pd.DataFrame, None): If the ``raw`` parameter is
            True, a list of tuples containing values is returned.
            Otherwise, a ``pandas.DataFrame`` object containing the
            returned data is returned.

            If this method is called with a script which does not return
            results, for example a CREATE script, None is returned;
            regardless of the value passed to the ``raw`` parameter.

        """
        # pylint: disable=no-else-return
        # pylint: disable=no-member
        try:
            with self._engine.connect() as conn:
                result = conn.execute(sa.text(stmt), params)
                conn.commit()
                conn.close()
            if raw:
                return result.fetchall()
            else:
                return self._result_to_df__cursor(result=result)
        except Exception as err:
            if 'object does not return rows' not in err._message():
                reporterror(err)
        return None

    def table_exists(self, table_name: str, verbose: bool=False) -> bool:
        """Using the ``engine`` object, test if the given table exists.

        Args:
            table_name (str): Name of the table to test.
            verbose (bool, optional): Print a message if the table does
                not exist. Defaults to False.

        Returns:
            bool: True if the given table exists, otherwise False.

        """
        params = {'schema': self._engine.url.database,
                  'table_name': table_name}
        stmt = ('select count(*) from information_schema.tables '
                'where table_schema = :schema '
                'and table_name = :table_name')
        exists = bool(self.execute_query(stmt, params=params, raw=True)[0][0])
        if (not exists) & verbose:
            msg = f'Table does not exist: {self._engine.url.database}.{table_name}'
            ui.print_warning(text=msg)
        return exists

    def _create_engine(self) -> sa.engine.base.Engine:
        """Create a database engine using the provided environment.

        Returns:
            sqlalchemy.engine.base.Engine: A sqlalchemy database engine
            object.

        """
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

    def _report_sqla_error(self, msg: str, error: SQLAlchemyError):  # pragma: nocover
        """Report SQLAlchemy error to the terminal.

        Args:
            msg (str): Additional error to be displayed. This message
                will be automatically prefixed with '[DatabaseError]: '
            error (sqlalchemy.exc.SQLAlchemyError): Caught error object
                from the try/except block.

        """
        # pylint: disable=unnecessary-dunder-call
        msg = f'\n{self._PREFIX} {msg}'
        stmt = f'- Statement: {error.statement}'
        errr = f'- Error: {error.orig.__str__()}'
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
            a ``sqlalchemy``/``mysql.connector`` procedure call.

        Returns:
            pd.DataFrame: A DataFrame containing the results from the
            procedure call.

        """
        df = pd.DataFrame()
        try:
            x = next(result)  # There is only one item in the iterable.
            df = pd.DataFrame(data=x.fetchall(), columns=x.column_names)
        except Exception as err:
            reporterror(err)
        return df
