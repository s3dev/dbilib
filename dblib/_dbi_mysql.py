#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Purpose:   This module contains the library's *MySQL* database methods
            and attribute accessors; which are a specialised version of
            the :class:`_db_base._DBIBase` class methods.

:Platform:  Linux/Windows | Python 3.6+
:Developer: J Berendt
:Email:     support@s3dev.uk

:Comments:  It's worth noting that the base module's core functionality
            was written for MySQL databases. Therefore, this
            MySQL-specific database class will modify this base class
            very little, if at all.

:Example:

    For class-specific useage examples, please refer to the docstring
    for the following classes:

        - :class:`_DBIMySQL`

"""
# pylint: disable=import-error

try:
    from _dbi_base import _DBIBase
except ImportError:
    from ._dbi_base import _DBIBase


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

            >>> from dblib.database import DBInterface

            class MyDB(DBInterface):

                def __init__(self, connstr: str):
                    super().__init__(connstr=('mysql+mysqlconnector://'
                                              '<user>:<pwd>@<host>:<port>/'
                                              '<db_name>'))

    """

    def __init__(self, connstr: str):
        """Class initialiser."""
        super().__init__(connstr=connstr)
