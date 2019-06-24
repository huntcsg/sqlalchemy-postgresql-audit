.. _naming_conventions:

Naming Conventions
==================

This library ships with the following default naming conventions. These can be overriden in the typical SQLAlchemy manner.

**audit.table**

.. autoattribute:: sqlalchemy_postgresql_audit.dialect.DEFAULT_AUDIT_TABLE_NAMING_CONVENTION
    :noindex:

**audit.function**

.. autoattribute:: sqlalchemy_postgresql_audit.dialect.DEFAULT_AUDIT_TABLE_FUNCTION_NAMING_CONVENTION
    :noindex:

**audit.trigger**

.. autoattribute:: sqlalchemy_postgresql_audit.dialect.DEFAULT_AUDIT_TABLE_TRIGGER_CONVENTION
    :noindex:

The `table_name` and the `schema` are the only data elements passed in to the format string.

Additionally, if the `schema` is `None`, then `"public"` is passed in.
