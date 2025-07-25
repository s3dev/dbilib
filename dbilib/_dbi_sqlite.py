#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module contains the library's *SQLite* database methods
            and attribute accessors; which are a specialised version of
            the :class:`_dbi_base._DBIBase` class methods.

:Platform:  Linux/Windows | Python 3.10+
:Developer: J Berendt
:Email:     support@s3dev.uk

:Comments:  n/a

:Example:

    For class-specific usage examples, please refer to the docstring
    for the following classes:

        - :class:`_DBISQLite`

"""
# Silence the spurious IDE-based error.
# pylint: disable=import-error

from utils4 import utils
from utils4.user_interface import ui
# locals
try:
    from ._dbi_base import _DBIBase
except ImportError:
    from _dbi_base import _DBIBase


class _DBISQLite(_DBIBase):
    """This *private* class holds the methods and properties which are
    used for accessing SQLite databases.

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
                    super().__init__(connstr=('sqlite:////path/to/database.db'))

    """

    def __init__(self, connstr: str):
        """SQLite database interface initialiser."""
        super().__init__(connstr=connstr)
        self._verify_db_exists()

    def table_exists(self, table_name: str, verbose: bool=False) -> bool:
        """Using the ``engine`` object, test if the given table exists.

        Args:
            table_name (str): Name of the table to test.
            verbose (bool, optional): Print a message if the table does
                not exist. Defaults to False.

        Returns:
            bool: True if the given table exists, otherwise False.

        """
        params = {'table_name': table_name}
        stmt = ('select count(*) from sqlite_master '
                'where type = \'table\' '
                'and name = :table_name')
        exists = bool(self.execute_query(stmt, params=params, raw=True)[0][0])
        if (not exists) & verbose:
            msg = f'Table does not exist: {self._engine.url.database}.{table_name}'
            ui.print_warning(text=msg)
        return exists

    def _verify_db_exists(self):
        """Verify the database file exists.

        Raises:
            FileNotFoundError: Raised if the database file passed via the
            connection string does not exist.

        """
        utils.fileexists(filepath=self.engine.url.database, error='raise')
