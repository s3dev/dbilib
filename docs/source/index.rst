============================
dbilib Library Documentation
============================

.. contents:: Page Contents
    :local:
    :depth: 1


.. _overview:

Overview
========
The ``dbilib`` library is a mid-level CPython database interface project
which is designed to fit between ``sqlalchemy`` and *your* database
interface library.

The interface exposes methods for easily executing SQL statements and
calling stored procedures - with minimal setup.

As of this release, the following database engines are supported:

- MySQL / MariaDB (via ``mysql-connector-python``)
- Oracle (via ``cx_Oracle``)
- SQLite3
- Microsoft SQL Server (via ``pyodbc``)

If you have any questions that are not covered by this documentation, or
if you spot any bugs, issues or have any recommendations, please feel free
to :ref:`contact us <contact-us>`.


.. _using-the-library:

Using the Library
=================

.. contents::
    :local:
    :depth: 1

This documentation suite contains detailed explanation and example usage
for each of the library's importable modules.

For detailed documentation, usage examples and links the source code
itself, please refer to the :ref:`library-api` page.

If there is a specific module or method which you cannot find, a
**search** field is built into the navigation bar to the left.

Database Support
----------------
Our currently supported databases are listed in the :ref:`overview`
section on this page. However, for further detail regarding the
databases supported by the `SQLAlchemy`_ library,
please refer to *their* documentation, specifically their
`Included Dialects`_ page, which lists the supported database dialects
and their version(s).


.. _connection-strings:

Connection Strings
------------------
For convenience, we have provided a link to the `connection string`_
(or database URL) templates for each database dialect supported by
``sqlalchemy``. Generally, the `database URLs`_ follow this convention::

    dialect+driver://username:password@host:port/database

For example, the MySQL / MariaDB specific database URL using the
``mysql-connector-python`` driver, is::

    mysql+mysqlconnector://<user>:<pwd>@<host>:<port>/<database>

Questions or Issues
-------------------
If you have any issues or questions with your installation, please refer
to the :ref:`troubleshooting` section, or feel free to
:ref:`contact us <contact-us>`.


.. _troubleshooting:

Troubleshooting
===============
No guidance at this time.


Documentation Contents
======================
.. toctree::
    :maxdepth: 1

    library
    changelog
    contact


Indices and Tables
==================
* :ref:`genindex`
* :ref:`modindex`


.. rubric:: Footnotes

.. _connection string: https://docs.sqlalchemy.org/en/20/core/engines.html#backend-specific-urls
.. _database URLs: https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls
.. _Included Dialects: https://docs.sqlalchemy.org/en/20/dialects/index.html#included-dialects
.. _SQLAlchemy: https://www.sqlalchemy.org/

|lastupdated|
