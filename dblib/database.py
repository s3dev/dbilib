#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module contains the library's database workers, and is
            the **entry point for the database accessors.**

:Platform:  Linux/Windows | Python 3.6+
:Developer: J Berendt
:Email:     support@s3dev.uk

:Comments:  As of v0.6.0, this module is *intentionally* **not**
            backwards-compatible with applications using
            versions < 0.6.0 as this module has been restructured for
            simplicity and to remove the dependency on the
            ``utils3.database`` module, which has been removed from
            ``utils4``.

:Example:
    Call a stored procedure, using the :class:`~Database` class::

        >>> from s3ddb.database import Database

        >>> dbo = Database('prod').<database_name>
        >>> dbo.call_procedure(proc='sp_get_some_stuff',
                               params=['a', 'b', 'c'])


    Execute a query using the database-specific *shortcut* accessor::

        >>> from s3ddb.database import adpidb

        # Access the database engine object.
        >>> apidb.engine
        Engine(mysql+mysqlconnector://api:***@XXX.XXX.XXX.XX:XXXX/api)

        # Execute a query using the engine.
        >>> resp = apidb.engine.execute('select count(*) from headers')
        >>> resp.fetchall()
        [(4,)]

"""
# pylint: disable=wrong-import-order

import pandas as pd
import sqlalchemy
import warnings
from mysql.connector.errors import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from typing import Union, Tuple
from utils4.reporterror import reporterror
from utils4.user_interface import ui
from s3ddb.environ import Environ


class _Generic:
    """This class holds the methods and properties which are used across
    all databases.  Each of the database-specific constructors inherits
    this class for its members.

    Args:
        environ (s3ddb.environ): The database-specific environ object.

    """

    _PREFIX = '\n[DatabaseError]:'

    def __init__(self, environ):
        """Class initialiser."""
        self._env = environ
        self._engine = self._create_engine()

    @property
    def engine(self):
        """The ``sqlalchemy.engine.base.Engine`` object."""
        return self._engine

    def call_procedure(self,
                       proc: str,
                       params: Union[list, tuple]=None,
                       return_status: bool=False) -> Union[pd.DataFrame,
                                                           Tuple[pd.DataFrame, bool]]:
        """Call a stored procedure, and return as DataFrame.

        Args:
            proc (str): Name of the stored procedure to call.
            params (Union[list, tuple], optional): A list (or tuple) of
                parameters to pass into the procedure. Defaults to None.
            return_status (bool, optional): Return the method's success
                status. Defaults to False.

        For example::

            >>> from s3ddb.database import apidb
            >>> df = apidb.call_procedure(proc='sp_procedure_name',
                                          params=['list', 'of', 'params'])

        Returns:
            Union[pd.DataFrame, Tuple[pd.DataFrame, bool]]:
            If the ``return_status`` argument is True, a tuple of the
            data and the method's return status is returned as::

                (data, status)

            Otherwise, the data is returned as a pd.DataFrame.

        """
        warnings.simplefilter('ignore')
        df = pd.DataFrame()
        success = False
        try:
            # v0.7.0.dev1: Updated to use a context manager in an
            # attempt to alleviate the '2055 Lost Connection' and
            # System Error 32 BrokenPipeError which occurs in mmaps.
            with self.engine.connect() as conn:
                cur = conn.connection.cursor(buffered=True)
                cur.callproc(proc, params)
                results = cur.stored_results()
                cur.close()
            df = self._stored_results_to_df(stored_results=results)
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
        """Call an **update** or **insert** stored procedure.

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
            # v0.7.0.dev1: Updated to use a context manager in an
            # attempt to alleviate the '2055 Lost Connection' and
            # System Error 32 BrokenPipeError which occurs in mmaps.
            with self.engine.connect() as conn:
                cur = conn.connection.cursor(buffered=True)
                cur.callproc(proc, params)
                if return_id:
                    cur.execute('SELECT LAST_INSERT_ID()')
                    rowid = cur.fetchone()[0]
                conn.connection.connection.commit()
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
        """Call an **update** or **insert** stored procedure for an iterable.

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
                cur = conn.connection.cursor(buffered=True)
                for i in iterable:
                    cur.callproc(proc, [*args, i])
                    conn.connection.connection.commit()
                cur.close()
                success = True
        except Exception as err:
            reporterror(err)
        return success

    def table_exists(self, table_name: str, verbose: bool=False) -> bool:
        """Using the ``engine`` object, test if the given table exists.

        This method is designed to be generic; being specialised to the
        currently instantiated database object.

        Args:
            table_name (str): Name of the table to test.
            verbose (bool, optional): Print a message if the table does
                not exist. Defaults to False.

        Returns:
            bool: True if the given table exists, otherwise False.

        """
        stmt = ("select count(*) from information_schema.tables "
                f"where table_schema = '{self._env.name}' and table_name = '{table_name}'")
        exists = bool(self.engine.execute(stmt).fetchall()[0][0])
        if (not exists) & verbose:
            ui.print_warning(text=f'Table does not exist: {self._env.name}.{table_name}')
        return exists

    def _create_engine(self) -> sqlalchemy.engine.base.Engine:
        """Create a database engine using the provided environment.

        Returns:
            sqlalchemy.engine.base.Engine: A sqlalchemy database engine
            object.

        """
        # v0.7.0: Added pool_* arguments to prevent MySQL timeout which
        #         causes the broken pipe and lost connection errors.
        return sqlalchemy.create_engine(url=self._env.connstr,
                                        poolclass=sqlalchemy.pool.QueuePool,
                                        pool_size=20,
                                        pool_recycle=3600,
                                        pool_timeout=30,
                                        pool_pre_ping=True,
                                        max_overflow=0)

    def _report_sqla_error(self, msg: str, error: SQLAlchemyError):
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
    def _stored_results_to_df(stored_results: object) -> pd.DataFrame:
        """Convert ``sqlalchemy`` USP results to a DataFrame.

        Args:
            stored_results (object): The ``cursor.stored_results()``
                object from a sqlalchemy procedure call.

        Returns:
            pd.DataFrame: A DataFrame containing the results from the
            USP.

        """
        data = {}
        cols = []
        df = pd.DataFrame()
        try:
            # Extract column names and data.
            for i in stored_results:
                cols = i.column_names
                data = i.fetchall()
            df = pd.DataFrame(data=data, columns=cols)
        except Exception as err:
            reporterror(err)
        return df


class _API(_Generic):
    """Constructor for the api database.

    Args:
        env (str): Setup the database for this environment.

    """

    def __init__(self, env: str):
        """Class initialiser."""
        self._environ = Environ(env=env).api
        super().__init__(environ=self._environ)


class _Mmaps(_Generic):
    """Constructor for the mmaps database.

    Args:
        env (str): Setup the database for this environment.

    """

    def __init__(self, env: str):
        """Class initialiser."""
        self._environ = Environ(env=env).mmaps
        super().__init__(environ=self._environ)


class _NetStat(_Generic):
    """Constructor for the netstat database.

    Args:
        env (str): Setup the database for this environment.

    """

    def __init__(self, env: str):
        """Class initialiser."""
        self._environ = Environ(env=env).netstat
        super().__init__(environ=self._environ)


class _PicLib(_Generic):
    """Constructor for the piclib database.

    Args:
        env (str): Setup the database for this environment.

    """

    def __init__(self, env: str):
        """Class initialiser."""
        self._environ = Environ(env=env).piclib
        super().__init__(environ=self._environ)


class _SADI(_Generic):
    """Constructor for the sadi database.

    Args:
        env (str): Setup the database for this environment.

    """

    def __init__(self, env: str):
        """Class initialiser."""
        self._environ = Environ(env=env).sadi
        super().__init__(environ=self._environ)


class _ServStat(_Generic):
    """Constructor for the servstat database.

    Args:
        env (str): Setup the database for this environment.

    """

    def __init__(self, env: str):
        """Class initialiser."""
        self._environ = Environ(env=env).servstat
        super().__init__(environ=self._environ)


class _SiteStat(_Generic):
    """Constructor for the sitestat database.

    Args:
        env (str): Setup the database for this environment.

    """

    def __init__(self, env: str):
        """Class initialiser."""
        self._environ = Environ(env=env).sitestat
        super().__init__(environ=self._environ)


class _WebStat(_Generic):
    """Constructor for the webstat database.

    Args:
        env (str): Setup the database for this environment.

    """

    def __init__(self, env: str):
        """Class initialiser."""
        self._environ = Environ(env=env).webstat
        super().__init__(environ=self._environ)


class Database:
    """
    This class serves as the entry point for the database accessors.

    Args:
        env (str, optional): Setup the database(s) for this environment.
            Defaults to 'prod'. Valid envs are: 'prod', 'dev'

    Note:
        A database connection **is not made** until the ``.connect()``
        method is called.

    Example:

        Call a stored procedure, using this :class:`~Database` class::

            >>> from s3ddb.database import Database

            >>> dbo = Database('prod').<database_name>
            >>> dbo.call_procedure(proc='sp_get_some_stuff',
                                   params=['a', 'b', 'c'])


        Execute a query using the database-specific *shortcut* accessor::

            >>> from s3ddb.database import adpidb

            # Access the database engine object.
            >>> apidb.engine
            Engine(mysql+mysqlconnector://api:***@XXX.XXX.XXX.XX:XXXX/api)

            # Execute a query using the engine.
            >>> resp = apidb.engine.execute('select count(*) from headers')
            >>> resp.fetchall()
            [(4,)]

    """

    def __init__(self, env: str='prod'):
        """Class initialiser."""
        self._api = _API(env=env)
        self._mmaps = _Mmaps(env=env)
        self._netstat = _NetStat(env=env)
        self._piclib = _PicLib(env=env)
        self._sadi = _SADI(env=env)
        self._servstat = _ServStat(env=env)
        self._sitestat = _SiteStat(env=env)
        self._webstat = _WebStat(env=env)

    @property
    def api(self):
        """The **api** database accessor."""
        return self._api

    @property
    def mmaps(self):
        """The **mmaps** database accessor."""
        return self._mmaps

    @property
    def netstat(self):
        """The **netstat** database accessor."""
        return self._netstat

    @property
    def piclib(self):
        """The **piclib** database accessor."""
        return self._piclib

    @property
    def sadi(self):
        """The **sadi** database accessor."""
        return self._sadi

    @property
    def servstat(self):
        """The **servstat** database accessor."""
        return self._servstat

    @property
    def sitestat(self):
        """The **sitestat** database accessor."""
        return self._sitestat

    @property
    def webstat(self):
        """The **webstat** database accessor."""
        return self._webstat


# Production databases.
apidb = _API(env='prod')
mmapsdb = _Mmaps(env='prod')
netstatdb = _NetStat(env='prod')
piclibdb = _PicLib(env='prod')
sadidb = _SADI(env='prod')
servstatdb = _ServStat(env='prod')
sitestatdb = _SiteStat(env='prod')
webstatdb = _WebStat(env='prod')
# Development databases.
apidb_dev = _API(env='dev')
mmapsdb_dev = _Mmaps(env='dev')
netstatdb_dev = _NetStat(env='dev')
piclibdb_dev = _PicLib(env='dev')
sadidb_dev = _SADI(env='dev')
servstatdb_dev = _ServStat(env='dev')
sitestatdb_dev = _SiteStat(env='dev')
webstatdb_dev = _WebStat(env='dev')
