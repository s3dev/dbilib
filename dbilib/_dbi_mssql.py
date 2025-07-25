#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module contains the library's *Microsoft SQL Server*
            database methods and attribute accessors; which are a
            specialised version of the :class:`_dbi_base._DBIBase` class
            methods.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt, J Preston
:Email:     support@s3dev.uk

:Comments:  n/a

:Example:

    For class-specific usage examples, please refer to the docstring
    for the following classes:

        - :class:`_DBIMSSQL`

"""
# pylint: disable=import-error

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.exc import SQLAlchemyError
from utils4.reporterror import reporterror
from utils4.user_interface import ui
# locals
try:
    from ._dbi_base import _DBIBase, ExitCode
except ImportError:
    from _dbi_base import _DBIBase, ExitCode


class _DBIMSSQL(_DBIBase):
    """This *private* class holds the methods and properties which are
    used for accessing Microsoft SQL Server databases.

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
                    super().__init__(connstr=('mssql+pyodbc://'
                                              '<user>:<pwd>@<host>:<port>/'
                                              '<db_name>'))


        'Userless' trusted connections can be used in the connection
        string as follows::

            >>> from dbilib.database import DBInterface

            class MyDB(DBInterface):

                def __init__(self, connstr: str):
                    super().__init__(connstr=('mssql+pyodbc'
                                              '://:@<host>:<port>/'
                                              '<dbname>'
                                              '?driver=<driver-name>'
                                              '&trusted_connection=yes'))

    """

    # The __init__ method is implemented in the parent class.

    def backup(self, table_name: str, verbose: bool=True) -> ExitCode:
        """Backup the given table to the backup database.

        Args:
            table_name (str): Name of the table to be backed up.
            verbose (bool, optional): Display helpful text indicating the
                status of the backup. Defaults to True.

        .. important::
            The backup database (which is implicitly determined by the
            engine's database name) **must** exist, or this method will
            fail. See below for the backup database's naming convention.

            Due to MSSQL's (interesting) handling of the
            ``CREATE DATABASE`` statement, the database cannot be created
            by this method for you; sorry.  Cheers MS!


        .. note::

            The backup database name is derived by prepending
            ``'__bak__'`` to the database name.

            This obfuscation was done intentionally to help prevent a
            user from click-selecting the wrong database (in SSMS) by
            accident.

        Returns:
            ExitCode: The exit code enumerator object associated to the
            status of the backup process.

        """
        bkdb = f'__bak__{self.database_name}'
        s1, s2, s3 = False, False, False
        s1 = self.table_exists(table_name=table_name, verbose=verbose)
        if s1: s2 = self.database_exists(database_name=bkdb, verbose=verbose)
        if s2: s3 = self._backup(table_name=table_name, bkdb_name=bkdb)
        if verbose: self._print_summary(success=all((s1, s2, s3)))
        if not s1: return ExitCode.ERR_BKUP_TBNEX
        if not s2: return ExitCode.ERR_BKUP_DBNEX
        if not s3: return ExitCode.ERR_BKUP_CKSUM
        return ExitCode.OK

    # pylint: disable=line-too-long
    def call_procedure(self,
                       proc: str,
                       *,
                       params: dict | tuple=None,
                       paramnames: list | tuple=None,
                       raw: bool=True,
                       return_status: bool=False) -> pd.DataFrame | tuple[pd.DataFrame | tuple, bool]:  # noqa  # pylint: disable=undefined-variable
        """Call a stored procedure, and return as a DataFrame.

        Args:
            proc (str): Name of the stored procedure to call.
            params (dict): A dictionary containing the parameter values
                to be used as key/value pairs, with the keys being the
                parameter names, and values being the data values passed
                into the procedure.
            paramnames (list|tuple, optional): An iterable object
                containing the procedure's parameter names, in order.
                Defaults to None. If not provided, these are collected
                from the database via the :meth:`get_parameter_names`
                method. For efficiency, the parameter names should be
                passed if making repeated calls to the procedure.
            raw (bool, optional): Return the data in 'raw' (tuple) format
                rather than as a formatted DataFrame. Defaults to True
                for efficiency.
            return_status (bool, optional): Return the method's success
                status. Defaults to False.

        Returns:
            pd.DataFrame | tuple[pd.DataFrame | tuple, bool]:
            If the ``return_status`` argument is True, a tuple of the
            data and the method's return status is returned as::

                (data, status)

            Otherwise, only the data is returned.

        """
        # pylint: disable=consider-using-f-string  # No, need the formatter.
        data = None
        success = False
        try:
            # Collect parameter names for the EXEC call if not provided.
            if not paramnames:
                paramnames = self.get_parameter_names(proc=proc)
            paramdef = ', '.join(map(':{}'.format, paramnames))
            with self.engine.connect() as con:
                resp = con.execute(sa.text(f'EXEC {proc} {paramdef}'), params)
                if resp.returns_rows:
                    if raw:
                        data = resp.fetchall()
                        success = bool(data)
                    else:
                        data = self._result_to_df__cursor(result=resp)
                        success = not data.empty
                con.close()
        except SQLAlchemyError as err:
            msg = f'Error occurred while running the USP: {proc}.'
            self._report_sa_error(msg=msg, error=err)
        except Exception as err:
            reporterror(error=err)
        return (data, success) if return_status else data

    def call_procedure_update(self,
                              proc: str,
                              *,
                              data: dict,
                              paramnames: list | tuple=None,
                              return_id: bool=False) -> bool | tuple:
        """Call an *update* or *insert* stored procedure.

        Note:
            Results are *not* returned from this call, only a boolean
            status flag and the optional last row ID, which **must be
            provided by the USP** if desired.

            If results are desired, please use the
            :meth:`~call_procedure` method.

        Args:
            proc (str): Name of the stored procedure to call.
            data (dict): A dictionary containing the data to be loaded
                as key/value pairs, with the keys being the parameter
                names, and values being the data values.
            paramnames (list|tuple, optional): An iterable object
                containing the procedure's parameter names, in order.
                Defaults to None. If not provided, these are collected
                from the database via the :meth:`get_parameter_names`
                method. For efficiency, the parameter names should be
                passed if making repeated calls to the procedure.
            return_id (bool, optional): Return the ID of the last
                inserted row. **See note above.** Defaults to False.

        Returns:
            bool | tuple: If ``return_id`` is False, True is
            returned if the procedure completed  successfully, otherwise
            False. If ``return_id`` is True, a tuple containing the
            ID of the last inserted row and the execution success flag
            are returned as::

                (id, success_flag)

        """
        # pylint: disable=consider-using-f-string  # No, need the formatter.
        try:
            success = False
            rowid = None
            # Collect parameter names for the EXEC call if not provided.
            if not paramnames:
                paramnames = self.get_parameter_names(proc=proc)
            params = ', '.join(map(':{}'.format, paramnames))
            with self.engine.connect() as con:
                resp = con.execute(sa.text(f'EXEC {proc} {params}'), data)
                if resp.returns_rows:
                    rowid = resp.fetchall()
                con.commit()
                con.close()
                success = True
        except Exception as err:
            reporterror(err)
        return (rowid, success) if return_id else success

    #
    # XXX: This has been left for possible future development.
    #      Currently a MySQL implementation.
    #
    # def call_procedure_update_many(self, *args, proc: str, iterable: list | tuple) -> bool:
    #     r"""Call an *update* or *insert* stored procedure for an iterable.

    #     Note:
    #         The arguments are passed into the USP in the following order:

    #             \*args, iterable_item

    #         Ensure the USP is designed to accept the iterable item as
    #         the *last* parameter.

    #     Args:
    #         *args (str | int | float): Positional arguments to be
    #             passed into the USP, in front of each iterable item.
    #             Note: The parameters are passed into the USP in the
    #             order received, followed by the iterable item.
    #         proc (str): Name of the stored procedure to call.
    #         iterable (list | tuple): List of items to be loaded into
    #             the database.

    #     Returns:
    #         bool: True if the update was successful, otherwise False.

    #     """
    #     try:
    #         success = False
    #         with self.engine.connect() as conn:
    #             cur = conn.connection.cursor()
    #             for i in iterable:
    #                 cur.callproc(proc, [*args, i])
    #                 conn.connection.connection.commit()
    #             cur.close()
    #             success = True
    #     except Exception as err:
    #         reporterror(err)
    #     return success

    def call_procedure_update_raw(self,
                                  proc: str,
                                  *,
                                  data: dict,
                                  paramnames: list | tuple=None) -> None:

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
            data (dict): A dictionary containing the data to be loaded
                as key/value pairs, with the keys being the parameter
                names, and values being the data values.
            paramnames (list|tuple, optional): An iterable object
                containing the procedure's parameter names, in order.
                Defaults to None. If not provided, these are collected
                from the database via the :meth:`get_parameter_names`
                method. For efficiency, the parameter names should be
                passed if making repeated calls to the procedure.

        """
        # pylint: disable=consider-using-f-string  # No, need the formatter.
        # Collect parameter names for the EXEC call if not provided.
        if not paramnames:
            paramnames = self.get_parameter_names(proc=proc)
        params = ', '.join(map(':{}'.format, paramnames))
        with self.engine.connect() as con:
            _ = con.execute(sa.text(f'EXEC {proc} {params}'), data)
            con.commit()
            con.close()

    def checksum(self, table_name: str, database_name: str=None) -> int | None:
        """Calculate a hash (checksum) on the given table.

        Args:
            table_name (str) Name of the table against which the checksum
                is to be calculated.
            database_name (str) Name of the database to use.
                This argument can be used if the table resides in a
                different database than the one to which the engine
                object already points. Defaults to None.

        This method wraps the ``CHECKSUM_AGG`` and ``BINARY_CHECKSUM``
        MSSQL functions.

        Returns:
            int | None: A signed integer representation of the table's
            hash value, if the table exists. Otherwise, None.

        """
        db = database_name if database_name else self.database_name
        stmt = f'SELECT CHECKSUM_AGG(BINARY_CHECKSUM(*)) FROM [{db}].[dbo].[{table_name}]'
        if all((not self._is_dangerous(stmt=stmt),
                self.table_exists(table_name=table_name, database_name=db))):
            return self.execute_query(stmt)[0][0]
        return None

    def database_exists(self, database_name: str, verbose: bool=False) -> bool:
        """Using the ``engine`` object, test if the given database exists.

        Args:
            database_name (str): Name of the database to test.
            verbose (bool, optional): Print a message if the database
                does not exist. Defaults to False.

        Returns:
            bool: True if the given database exists, otherwise False.

        """
        exists = False
        stmt = f'select count(*) from [sys].[databases] where [name] = \'{database_name}\''
        if not self._is_dangerous(stmt=stmt):
            exists = bool(self.execute_query(stmt, raw=True)[0][0])
            if (not exists) & verbose:
                msg = f'Database does not exist: {database_name}'
                ui.print_warning(text=msg)
        return exists

    def get_parameter_names(self, proc: str) -> tuple:
        """Retrieve the parameter names for the given USP.

        For portability, this method has been updated to use an embedded
        query rather than a USP.

        Args:
            proc (str): Name of the target stored procedure.

        Returns:
            tuple: A tuple of parameter names for the given USP.

        """
        # TODO: Make this more robust by removing the hardcoded SUBSTRING and
        #       test if the first char is '@' before removing.
        stmt = f"""
            /* Use SUBSTRING to remove the '@' from the parameter name. */
            SELECT
                SUBSTRING([name], 2, 99) AS parameters
            FROM
                [sys].[parameters]
            WHERE
                [object_id] = ( SELECT [object_id] FROM [sys].[objects] WHERE [name] = '{proc}' )
            ORDER BY
                [parameter_id];
        """
        if not self._is_dangerous(stmt=stmt):
            resp = self.execute_query(stmt=stmt, raw=True)
            if resp:
                return next(zip(*resp))
            return ()
        return ()  # pragma: nocover  # Unreachable

    def table_exists(self, table_name: str, database_name: str=None, verbose: bool=False) -> bool:
        """Using the ``engine`` object, test if the given table exists.

        Args:
            table_name (str): Name of the table to test.
            database_name (str) Name of the database to use.
                This argument can be used if the table resides in a
                different database than the one to which the engine
                object already points. Defaults to None.
            verbose (bool, optional): Print a message if the table does
                not exist. Defaults to False.

        Returns:
            bool: True if the given table exists, otherwise False.

        """
        exists = False
        db = database_name if database_name else self.database_name
        params = {
                  'table_catalog': db,
                  'table_name': table_name,
                  'table_schema': 'dbo',
                 }
        stmt = (f'select count(*) from [{db}].[information_schema].[tables] '
                'where table_catalog = :table_catalog '
                'and table_schema = :table_schema '
                'and table_name = :table_name')
        if not self._is_dangerous(stmt=stmt):
            exists = bool(self.execute_query(stmt, params=params, raw=True)[0][0])
            if (not exists) & verbose:
                msg = f'Table does not exist: {db}.{table_name}'
                ui.print_warning(text=msg)
        return exists

    def _backup(self, table_name: str, bkdb_name: str) -> bool:
        """Perform the table backup to the backup database.

        Args:
            table_name (str): Name of the table to be backed up.
            bkdb_name (str): Name of the backup database.

        Returns:
            bool: True if the backup was successful, otherwise False.
            A successful backup is determined by verifying matching table
            checksum values between the origin and backup tables.

        """
        stmt1 = f'DROP TABLE IF EXISTS [{bkdb_name}].[dbo].[{table_name}]'
        stmt2 = f'SELECT * INTO [{bkdb_name}].[dbo].[{table_name}] FROM [dbo].[{table_name}]'
        if all((not self._is_dangerous(stmt=stmt1), not self._is_dangerous(stmt=stmt2))):
            self.execute_query(stmt1)
            self.execute_query(stmt2)
        ck1 = self.checksum(table_name=table_name, database_name=self.database_name)
        ck2 = self.checksum(table_name=table_name, database_name=bkdb_name)
        return ck1 == ck2

    @staticmethod
    def _print_summary(success: bool) -> None:
        """Print a short end-of-processing summary.

        Args:
            success (bool): Flag indicating if the backup was successful.

        This message is designed to be short and concise, as the backup
        is designed to be called by other applications, so a short
        message is preferable.

        """
        if success:
            ui.print_normal('Table backup successful.')
        else:
            ui.print_warning('Table backup failed.')
