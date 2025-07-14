# A generalised and simple database interface library

[![PyPI - Version](https://img.shields.io/pypi/v/dbilib?style=flat-square)](https://pypi.org/project/dbilib)
[![PyPI - Implementation](https://img.shields.io/pypi/implementation/dbilib?style=flat-square)](https://pypi.org/project/dbilib)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dbilib?style=flat-square)](https://pypi.org/project/dbilib)
[![PyPI - Status](https://img.shields.io/pypi/status/dbilib?style=flat-square)](https://pypi.org/project/dbilib)
[![Static Badge](https://img.shields.io/badge/tests-passing-brightgreen?style=flat-square)](https://pypi.org/project/dbilib)
[![Static Badge](https://img.shields.io/badge/code_coverage-100%25-brightgreen?style=flat-square)](https://pypi.org/project/dbilib)
[![Static Badge](https://img.shields.io/badge/pylint_analysis-100%25-brightgreen?style=flat-square)](https://pypi.org/project/dbilib)
[![Documentation Status](https://readthedocs.org/projects/dbilib/badge/?version=latest&style=flat-square)](https://dbilib.readthedocs.io/en/latest/)
[![PyPI - License](https://img.shields.io/pypi/l/dbilib?style=flat-square)](https://opensource.org/licenses/MIT)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/dbilib?style=flat-square)](https://pypi.org/project/dbilib)

The ``dbilib`` project is a mid-level CPython database interface library which is designed to fit between ``sqlalchemy`` and *your* database interface library.

The interface exposes methods for easily accessing the database engine, executing SQL statements and calling stored procedures - with minimal setup.

As of this release, the following database engines are supported:

- MySQL / MariaDB (via `mysql-connector-python`)
- Oracle (via `cx_Oracle`)
- SQLite3
- Microsoft SQL Server (via `pyodbc`)


## Installation
Installing the library is as easy as:

```
pip install dbilib
```
This will install the library's required dependencies (e.g. `sqlalchemy`, etc.). However, it will *not* install the database-specific libraries, (e.g. `cx_Oracle`, `mysql-connector-python`, `pyodbc`, etc).  This design feature helps to not bloat your environment with unneeded packages and keeps cross-platform capability and flexibility.


## Using the Library
The [documentation suite](https://dbilib.readthedocs.io/en/latest/index.html) contains usage examples and detailed explanation for each of the library's importable modules. Please refer to the [Library API Documentation](https://dbilib.readthedocs.io/en/latest/library.html) section of the documentation.


## Database Support
Our currently supported databases are listed in the overview section on this page. However, for further detail regarding the databases supported by the [SQLAlchemy](https://www.sqlalchemy.org/) library, please refer to *their* documentation, specifically their [Included Dialects](https://docs.sqlalchemy.org/en/20/dialects/index.html#included-dialects) page, which lists the supported database dialects and their version(s).

### Connection Strings
For convenience, we have provided a link to the [connection string](https://docs.sqlalchemy.org/en/20/core/engines.html#backend-specific-urls) (or database URL) templates for each database dialect supported by `sqlalchemy`. Generally, the [database URLs](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls) follow this convention:

```
dialect+driver://username:password@host:port/database
```

For example, the MySQL / MariaDB specific database URL using the ``mysql-connector-python`` driver, is:

```
mysql+mysqlconnector://<user>:<pwd>@<host>:<port>/<database>
```
