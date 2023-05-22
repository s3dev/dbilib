#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module provides the library's primary entry-point for
            accessing the database methods and attributes.

:Platform:  Linux/Windows | Python 3.6+
:Developer: J Berendt
:Email:     support@s3dev.uk

:Comments:  n/a

:Example:

    For class-specific useage examples, please refer to the docstring
    for the following classes:

        - :class:`DBInterface`

"""
# pylint: disable=import-error

import sqlalchemy as sa
from utils4 import utils
# locals
if utils.testimport('mysql', verbose=False):
    try:
        from _dbi_mysql import _DBIMySQL
    except ImportError:
        from ._dbi_mysql import _DBIMySQL
if utils.testimport('cx_oracle', verbose=False):
    try:
        from _dbi_oracle import _DBIOracle
    except ImportError:
        from ._dbi_oracle import _DBIOracle


class DBInterface:
    """This class holds the methods and properties which are used across
    all databases. This class is the primary entry-point for the database
    interface.

    Database-specific functionality is provided by this class'
    :meth:``__new__`` method, which returns the appropriate instance of
    the lower-level database-specifc class, depending on the connection
    string provided. Or, more specifically, the ``sqlalchemy.Engine``
    object created from the provided connection string.

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
    # pylint: disable=unused-argument

    _SUPPORTED_DBS = ['mysql', 'oracle']

    def __new__(cls, connstr: str, *args, **kwargs):
        """Provide a database interface based on the connection string.

        Using the provided connection string, a
        ``sqlalchemy.engine.base.Engine`` object is created. Using the
        ``.name`` attribute, an instance of the associated database
        interface class is returned.

        For example, if the ``.name`` attribute is ``'mysql'``, an
        instance of the :class:`_db_mysql._DBIMySQL` private interface
        class is returned. Likewise, if the ``.name`` attribute is
        ``'oracle'``, an instance of the :class:`_db_oracle._DBIOracle`
        private interface class is returned, etc.

        Args:
            connstr (str): The SQLAlchemy-syle connection string, from
                which the ``sqlalchemy.engine.base.Engine`` is created
                for the database interface instance.

        """
        # pylint: disable=no-else-return
        name = cls._create_engine__internal_only(connstr=connstr)
        if name not in cls._SUPPORTED_DBS:
            raise NotImplementedError('The only databases supported at this time are: '
                                      f'{cls._SUPPORTED_DBS}.')
        if all((name == 'mysql', utils.testimport('mysql.connector', verbose=False))):
            return _DBIMySQL(connstr=connstr)
        elif all((name == 'oracle', utils.testimport('cx_oracle', verbose=False))):
            return _DBIOracle(connstr=connstr)
        else:
            raise RuntimeError('An error occurred while creating an instance of the database '
                               'accessor class. Perhaps the appropriate database driver is not '
                               'installed?')
        return None

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
