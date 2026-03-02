#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module contains the library's *Oracle* database methods
            and attribute accessors; which are a specialised version of
            the :class:`_dbi_base._DBIBase` class methods.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     support@s3dev.uk

:Comments:  n/a

:Example:

    For class-specific usage examples, please refer to the docstring
    for the following classes:

        - :class:`_DBIOracle`

"""
# pylint: disable=wrong-import-order
# Silence the spurious IDE-based error.
# pylint: disable=import-error

import cx_Oracle
import pandas as pd
from utils4.reporterror import reporterror
from utils4.user_interface import ui
# locals
try:
    from ._dbi_base import _DBIBase
except ImportError:
    from _dbi_base import _DBIBase


class _DBIOracle(_DBIBase):
    """This *private* class holds the methods and properties which are
    used for accessing Oracle databases.

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
                    super().__init__(connstr=('oracle+cx_oracle://'
                                              '<user>:<pwd>'
                                              '@(DESCRIPTION=(ADDRESS='
                                              '(PROTOCOL=TCP)'
                                              '(HOST=<host>)'
                                              '(PORT=<port>))'
                                              '(CONNECT_DATA='
                                              '(SERVICE_NAME=<svcname>)))'))

    """

    _ERROR_NI = ('Due to restrictions on the development environment, '
                 'this method is currently not implemented.')

    # The __init__ method is implemented in the parent class.

    def call_procedure(self,
                       proc: str,
                       params: list | tuple = None,
                       return_status: bool=False) -> pd.DataFrame | tuple[pd.DataFrame | bool]:
        """Call a stored procedure, and return as a DataFrame.

        Args:
            proc (str): Name of the stored procedure to call.
            params (list | tuple, optional): A list (or tuple) of
                parameters to pass into the procedure. Defaults to None.
            return_status (bool, optional): Return the method's success
                status. Defaults to False.

        Returns:
            pd.DataFrame | tuple[pd.DataFrame | bool]:
            If the ``return_status`` argument is True, a tuple of the
            data and the method's return status is returned as::

                (df, status)

            Otherwise, only the data is returned, as a pd.DataFrame.

        """
        df = pd.DataFrame()
        success = False
        try:
            with self.engine.connect() as conn:
                cur = conn.connection.cursor()
                refcur = conn.connection.cursor()
                cur.callproc(proc, params + [refcur])
                conn.connection.connection.commit()
            df = self._result_to_df__refcursor(refcur=refcur)
            cur.close()
            refcur.close()
            success = not df.empty
        except cx_Oracle.DatabaseError as err:
            msg = f'Error occurred while running the USP: {proc}.'
            self._report_cxo_error(msg=msg, error=err)
        except Exception as err:
            reporterror(error=err)
        return (df, success) if return_status else df

    def call_procedure_update(self):
        """Call an *update* or *insert* stored procedure.

        Warning:
            Due to the restrictions on the Oracle development
            environment, database UPDATE-like methods are not allowed.
            Therefore, this method is *currently* not implemented.

        Raises:
            NotImplementedError: Warn the user that this method is
            currently not implemented.

        """
        raise NotImplementedError(self._ERROR_NI)

    def call_procedure_update_many(self):
        """Call an *update* or *insert* stored procedure for an iterable.

        Warning:
            Due to the restrictions on the Oracle development
            environment, database UPDATE-like methods are not allowed.
            Therefore, this method is *currently* not implemented.

        Raises:
            NotImplementedError: Warn the user that this method is
            currently not implemented.

        """
        raise NotImplementedError(self._ERROR_NI)

    def call_procedure_update_raw(self):
        """Call an *update* or *insert* stored procedure, without error
        handling.

        Warning:
            Due to the restrictions on the Oracle development
            environment, database UPDATE-like methods are not allowed.
            Therefore, this method is *currently* not implemented.

        Raises:
            NotImplementedError: Warn the user that this method is
            currently not implemented.

        """
        raise NotImplementedError(self._ERROR_NI)

    def table_exists(self, table_name: str, verbose: bool=False) -> bool:
        """Using the ``engine`` object, test if the given table exists.

        Args:
            table_name (str): Name of the table to test.
            verbose (bool, optional): Print a message if the table does
                not exist. Defaults to False.

        Note:
            As most Oracle objects are UPPERCASE, the table name is converted
            to upper case before being passed into the query.

        Returns:
            bool: True if the given table exists, otherwise False.

        """
        params = {'table_name': table_name.upper()}
        stmt = 'select count(*) from all_tables where table_name = :table_name'
        exists = bool(self.execute_query(stmt, params=params, raw=True)[0][0])
        if (not exists) & verbose:
            msg = f'Table does not exist: {table_name}, for user {self._engine.url.username}.'
            ui.print_warning(text=msg)
        return exists

    def _report_cxo_error(self, msg: str, error: cx_Oracle.DatabaseError):
        """Report cx_Oracle error to the terminal.

        Args:
            msg (str): Additional error to be displayed. This message
                will be automatically prefixed with '[DatabaseError]: '
            error (cx_Oracle.DatabaseError): Caught error object from the
                try/except block.

        """
        msg = f'{self._PREFIX} {msg}'
        errr = f'- Error: {error.args[0].message}'
        ui.print_alert(text=msg)
        ui.print_alert(text=errr)

    @staticmethod
    def _result_to_df__refcursor(refcur: cx_Oracle.Cursor) -> pd.DataFrame:
        """Convert a ``cx_Oracle.Cursor`` object to a DataFrame.

        If the cursor did not return results, an empty DataFrame
        containing the column names only, is returned.

        Args:
            refcur (cx_Oracle.Cursor): Object to be converted.

        Returns:
            pd.DataFrame: A ``pandas.DataFrame`` object containing the
            cursor's data.

        """
        return pd.DataFrame(refcur, columns=[i[0] for i in refcur.description])
