#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the library's primary entry-point for
            accessing the database methods and attributes.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     support@s3dev.uk

:Comments:  n/a

:Example:

    For class-specific usage examples, please refer to the docstring
    for the following classes:

        - :class:`DBInterface`

"""
# This enables a single module installed test, rather than two.
# pylint: disable=import-outside-toplevel
# Silence the spurious IDE-based error.
# pylint: disable=import-error

import os
import sys
import sqlalchemy as sa
from utils4 import utils

# Set syspath to enable the private modules to import their db-specific class.
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))


class DBInterface:
    """This class holds the methods and properties which are used across
    all databases. This class is the primary entry-point for the database
    interface.

    Database-specific functionality is provided by this class'
    :meth:`__new__` method, which returns the appropriate instance of
    the lower-level database-specific class, depending on the connection
    string provided. Or, more specifically, the ``sqlalchemy.Engine``
    object created from the provided connection string.

    Note:
        Due to the way this class is created - for specific design
        reasons - the inheriting class' ``__init__`` method **will not
        be called**. Therefore, specialisation is not as simple as
        inheritance and calling the ``super()`` function.

        See the examples below for a use-case in how to specialise this
        class with your own methods.

    Args:
        connstr (str): The database-specific SQLAlchemy connection
            string.

    :Example Use:

        This low-level generalised class is designed to be instantiated
        by local program or database module, as::

            >>> from dbilib.database import DBInterface

            >>> dbi = DBInterface(connstr=('mysql+mysqlconnector://'
                                           '<user>:<pwd>@<host>:<port>/'
                                           '<db_name>'))
            >>> dbi.engine
            Engine(mysql+mysqlconnector://<user>:***@<host>:<port>/db_name)


        For example, the ``dbi`` instance can be used to execute a
        query, as::

            >>> result = dbi.execute_query('SELECT COUNT(*) FROM mytable');
            >>> result
            [(14,)]


        Additionally, the ``dbi.engine`` object can be supplied to the
        :func:`pandas.read_sql` function's ``con`` parameter, as the
        database connection object, as::

            >>> import pandas as pd

            >>> sql = 'select count(*) from mytable'
            >>> df = pd.read_sql(sql, con=dbi.engine)

            >>> df
                count(*)
             0        14

    :Subclass Specialisation:

        To *specialise the subclass*, a bit of 'pseudo-inheritance' is
        required due to the way the :class:`DBInterface` class is
        created. A 'standard inheritance' with a call to ``super()``
        does not work, as the subclass' ``__init__`` method is **not**
        called. Therefore, the subclass must add the parent's attributes
        into its class, manually.

        This can be done as follows::

            from dbilib.database import DBInterface

            class MyDBI:

                def __init__(self, connstr: str):
                    #
                    # Pseudo-inherit the DBInterface class by 'copying'
                    # the attributes into this subclass.
                    #
                    # There are many ways to do this. This is the most
                    # general, as functions, methods and properties are
                    # captured.
                    #
                    self._dbi = DBInterface(connstr=connstr)
                    fns = [fn for fn in dir(self._dbi) if not fn.startswith('__')]
                    for fn in fns:
                        setattr(self, fn, self._dbi.__getattribute__(fn))

                @property
                def spam(self):
                    return 'spam'

                # Continuation of class definition ...

            >>> db = MyDBI(connstr=('mysql+mysqlconnector://'
                                    '<user>:<pwd>@<host>:<port>/'
                                    '<db_name>'))
            # List the database interface class' attributes.
            # Notice that 'spam' is included in the list, along with the
            # methods from the :class:`DBInterface` class, thus
            # *simulating* inheritance.
            >>> dir(db)
            ['_PREFIX',
             '__class__',
             '__delattr__',
             ...,
             '__str__',
             '__subclasshook__',
             '__weakref__',
             '_connstr',
             '_create_engine',
             '_dbi',
             '_engine',
             '_report_sa_error',
             '_result_to_df__cursor',
             '_result_to_df__stored',
             'call_procedure',
             'call_procedure_update',
             'call_procedure_update_many',
             'call_procedure_update_raw',
             'database_name',
             'engine',
             'execute_query',
             'spam',           # <---
             'table_exists']]

    """

    _SUPPORTED_DBS = ['mssql', 'mysql', 'oracle', 'sqlite']

    def __new__(cls, connstr: str, *args, **kwargs):
        """Provide a database interface based on the connection string.

        Using the provided connection string, a
        ``sqlalchemy.engine.base.Engine`` object is created. Using the
        ``.name`` attribute, an instance of the associated database
        interface class is returned.

        For example, if the ``.name`` attribute is ``'mysql'``, an
        instance of the :class:`_dbi_mysql._DBIMySQL` private interface
        class is returned. Likewise, if the ``.name`` attribute is
        ``'oracle'``, an instance of the :class:`_dbi_oracle._DBIOracle`
        private interface class is returned, etc.

        Args:
            connstr (str): The SQLAlchemy-syle connection string, from
                which the ``sqlalchemy.engine.base.Engine`` is created
                for the database interface instance.

        """
        # Enable the use of *args and **kwargs for class parameters.
        # pylint: disable=unused-argument
        name = cls._create_engine__internal_only(connstr=connstr)
        if name not in cls._SUPPORTED_DBS:
            raise NotImplementedError('The only databases supported at this time are: '
                                      f'{cls._SUPPORTED_DBS}.')
        # These are intentionally verbose as a ModuleNotFoundError will
        # be raised during the test if operating on an environment without
        # that driver installed.
        if name == 'mssql':
            if utils.testimport('pyodbc', verbose=False):
                from _dbi_mssql import _DBIMSSQL
                return _DBIMSSQL(connstr=connstr, *args, **kwargs)
        if name == 'mysql':
            if utils.testimport('mysql.connector', verbose=False):
                from _dbi_mysql import _DBIMySQL
                return _DBIMySQL(connstr=connstr, *args, **kwargs)
        if name == 'oracle':  # pragma: nocover
            if utils.testimport('cx_Oracle', verbose=False):
                from _dbi_oracle import _DBIOracle
                return _DBIOracle(connstr=connstr, *args, **kwargs)
        if name == 'sqlite':
            if utils.testimport('sqlite3', verbose=False):
                from _dbi_sqlite import _DBISQLite
                return _DBISQLite(connstr=connstr, *args, **kwargs)
        # Fallback if a module is not installed.
        # This is actually caught by the _create_engine__internal_only method.
        raise RuntimeError('An error occurred while creating an instance of the database '
                           'accessor class. Perhaps the appropriate database driver is not '
                           'installed?')  # pragma: nocover  (never reached)

    @staticmethod
    def _create_engine__internal_only(connstr: str) -> str:
        """Create a database engine using the provided connection string.

        Warning:
            This method is *not* to be called independently as:

                - The engine itself is not returned.
                - The connect is disposed immediately after creation.
                - The ``pool_*`` objects are not set.

            The engine created here is *only* meant to providing
            database-class routing for this class' :meth:`__new__`
            method.

        Args:
            connstr (str): The SQLAlchemy connection string.

        Returns:
            str: The value of the ``.name`` attribute from the database
            engine.

        """
        _engine = sa.create_engine(url=connstr)
        name = _engine.name.lower()
        _engine.dispose(close=True)
        return name
