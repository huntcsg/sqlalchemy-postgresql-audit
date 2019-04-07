# SQLAlchemy Postgresql Audit

[![CircleCI](https://circleci.com/gh/huntcsg/sqlalchemy-postgresql-audit.svg?style=svg)](https://circleci.com/gh/huntcsg/sqlalchemy-postgresql-audit) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/a80daeed20654e7aa85358d8e9c761cf)](https://www.codacy.com/app/fool.of.god/sqlalchemy-postgresql-audit?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=huntcsg/sqlalchemy-postgresql-audit&amp;utm_campaign=Badge_Grade) [![codecov](https://codecov.io/gh/huntcsg/sqlalchemy-postgresql-audit/branch/master/graph/badge.svg)](https://codecov.io/gh/huntcsg/sqlalchemy-postgresql-audit)

## Description

Enables table change tracking support for tables defined by SQLAlchemy models.

Additionally, provides a flexible mechanism for enriching table change data with additional metadata (such as a request UUID or a username or ID).

## Implementation

After registering the relevant SQLAlchemy event listeners, whenever a table is attached to a metadata object, it's info will be checked for specific keys indicating that the table should be audited. If so, a table similar to the source table will be created, with the same name and types (but no constraints or nullability requirements). Additionally, an operation indicator (I, U, D for insert, update, delete) and a DB timestamp will be included as columns.
A function and trigger definition are then also defined to insert a row into the audit table whenever a row is inserted, updated, or deleted. For inserts and updates, the row in the audit table is the NEW row representation. For deletes, the row in the audit table is the OLD row.
While any typical create_all/drop_all command will create/drop the relevant tables, Audit Tables info dictionary also contains the DDL necessary to create and drop the function and trigger, and any migration mechanism in usage would need to take advantage of this DDL how it sees fit.

In order to enrich the change data with relevant metadata (such as an application user id or a webrequest UUID, etc), the procedure can be configured (via the table info) to reference any number of session local variables. These variables will be written in the `audit.*` namespace.  Helper functions are provided for setting these these session variables, and it is recommended that you integrate these deeply in your sessionmaking logic.  

## Installation

```bash
pip install sqlalchemy-postgresql-audit
```

This is only known to be compatible with the `postgresql+psycopg2` dialect.

## Usage

This package "claims" keys in `info` at 'audit.*'. 

In order for your table definitions to be ready, you must indicate in the info dictionary to enable the table audit mechanism.

```python
from sqlalchemy import MetaData, Table, Column, String
import sqlalchemy_postgresql_audit.event_listeners.sqlalchemy


meta = MetaData()

# You must install the event listeners prior to associating any tables with the metadata object.
sqlalchemy_postgresql_audit.event_listeners.sqlalchemy.install()

foo = Table(
        "foo",
        meta,
        Column("bar", String),
        info={
            "audit.options": {
                "enabled": True,
            }
        }
    )
```

This code will result in an additional table definition being added to the meta data object

An example create statement (if you created this table) is:

```sql
CREATE TABLE public.foo_audit (
        audit_operation VARCHAR(1) NOT NULL, 
        audit_operation_timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
        bar VARCHAR
)
```

## Naming Conventions

You can find the default naming conventions at 

```python
from sqlalchemy_postgresql_audit import (
    DEFAULT_AUDIT_TABLE_NAMING_CONVENTION, 
    DEFAULT_AUDIT_TABLE_FUNCTION_NAMING_CONVENTION, 
    DEFAULT_AUDIT_TABLE_TRIGGER_CONVENTION,
)

```

These can overridden by passing a naming convention format string to the `naming_conventions` dictionary under the relevant `audit.table`, `audit.function`, or `audit.trigger` conventions.

```python
from sqlalchemy import MetaData
from sqlalchemy.util import immutabledict
NAMING_CONVENTIONS = immutabledict(
    {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
        "audit.table": "%(table_name)s_audr",
    }
)

meta = MetaData(naming_convention=NAMING_CONVENTIONS)
```

## Session Settings

```python
from sqlalchemy import MetaData, Column, Table, String
from sqlalchemy.dialects.postgresql import UUID
meta = MetaData()

foo = Table(
    "foo",
    meta,
    Column("bar", String),
    info={
        "audit.options": {
            "enabled": True,
            'session_settings': [
                Column('username', String, nullable=False),
                Column('app_uuid', UUID),
            ]
        }
    },
    schema="public",
)
```

which resulted in the following audit table being created:

```sql
CREATE TABLE public.foo_audr (
        audit_operation VARCHAR(1) NOT NULL, 
        audit_operation_timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
        username VARCHAR NOT NULL, 
        app_uuid UUID, 
        bar VARCHAR
)
```

## Include as a SQLAlchemy plugin

You can include this as a plugin at the `audit` name

### Via the connection string

```python
from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg2://user:password@host:port/dbname?plugin=audit")
```
### Via the create_engine option

```python
from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg2://user:password@host:port/dbname", plugins=['audit'])
```



## Alembic Integration

This library is partially integrated with alembic. Some aspects are not perfect (downgrades drop the triggers and function and don't replace them)
