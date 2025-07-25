#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module contains the library's *MySQL* database methods
            and attribute accessors; which are a specialised version of
            the :class:`_dbi_base._DBIBase` class methods.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     support@s3dev.uk

:Comments:  n/a

:Example:

    For class-specific usage examples, please refer to the docstring
    for the following classes:

        - :class:`_DBIMySQL`

"""
# pylint: disable=wrong-import-order
# Silence the spurious IDE-based error.
# pylint: disable=import-error

import pandas as pd
import warnings
from mysql.connector.errors import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from utils4.reporterror import reporterror
from utils4.user_interface import ui
# locals
try:
    from ._dbi_base import _DBIBase
except ImportError:
    from _dbi_base import _DBIBase


class _DBIMySQL(_DBIBase):
    """This *private* class holds the methods and properties which are
    used for accessing MySQL-like databases, including MariaDB.

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
        warnings.simplefilter('ignore')
        df = pd.DataFrame()
        success = False
        try:
            # Use a context manager in an attempt to alleviate the
            # '2055 Lost Connection' and System Error 32 BrokenPipeError.
            with self.engine.connect() as conn:
                cur = conn.connection.cursor(buffered=True)
                cur.callproc(proc, params)
                result = cur.stored_results()
                conn.connection.connection.commit()
                cur.close()
            df = self._result_to_df__stored(result=result)
            success = not df.empty
        except SQLAlchemyError as err:
            msg = f'Error occurred while running the USP: {proc}.'
            self._report_sa_error(msg=msg, error=err)
        except Exception as err:
            reporterror(error=err)
        return (df, success) if return_status else df

    def call_procedure_update(self,
                              proc: str,
                              params: list=None,
                              return_id: bool=False) -> bool | tuple:
        """Call an *update* or *insert* stored procedure.

        Note:
            Results are *not* returned from this call, only a boolean
            status flag and the optional last row ID.

            If results are desired, please use the
            :meth:`~call_procedure` method.

        Args:
            proc (str): Name of the stored procedure to call.
            params (list, optional): A list of parameters to pass into
                the USP. Defaults to None.
            return_id (bool, optional): Return the ID of the last
                inserted row. Defaults to False.

        Returns:
            bool | tuple: If ``return_id`` is False, True is
            returned if the procedure completed  successfully, otherwise
            False. If ``return_id`` is True, a tuple containing the
            ID of the last inserted row and the execution success flag
            are returned as::

                (id, success_flag)

        """
        try:
            rowid = None
            success = False
            # Use a context manager in an attempt to alleviate the
            # '2055 Lost Connection' and System Error 32 BrokenPipeError.
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

    def call_procedure_update_many(self, *args, proc: str, iterable: list | tuple) -> bool:
        r"""Call an *update* or *insert* stored procedure for an iterable.

        Note:
            The arguments are passed into the USP in the following order:

                \*args, iterable_item

            Ensure the USP is designed to accept the iterable item as
            the *last* parameter.

        Args:
            *args (str | int | float): Positional arguments to be
                passed into the USP, in front of each iterable item.
                Note: The parameters are passed into the USP in the
                order received, followed by the iterable item.
            proc (str): Name of the stored procedure to call.
            iterable (list | tuple): List of items to be loaded into
                the database.

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
            proc (str): Name of the stored procedure to call.
            params (list, optional): A list of parameters to pass into
                the USP. Defaults to None.

        """
        with self._engine.connect() as conn:
            cur = conn.connection.cursor(buffered=True)
            cur.callproc(proc, params)
            conn.connection.connection.commit()
            cur.close()

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
