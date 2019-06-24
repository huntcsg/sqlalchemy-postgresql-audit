Example
=======

This example represents a full workable implementation.


First, we set up naming conventions and enable the audit features

.. code-block:: python

    from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine
    from sqlalchemy.dialects.postgresql import UUID
    from sqlalchemy.engine.url import URL
    from sqlalchemy.util import immutabledict
    import sqlalchemy_postgresql_audit


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

    # Event listeners must be enabled before tables are added to the Metadata Object
    sqlalchemy_postgresql_audit.enable()

    meta = MetaData(naming_convention=NAMING_CONVENTIONS)

Next we add a simple table to the metadata, and enable auditing on this table by setting `enabled` to `True` in the `audit.options` dictionary of the `info` attribute.

.. code-block:: python

    bar = Table(
        "bar",
        meta,
        Column("foo", String),
        info={
            "audit.options": {
                "enabled": True
            }
        },
    )

We add another table, and this one we want to also capture some data we will set in the local session settings.

Notice that `username` is not nullable, so that *must* be set in the session or any changes to this table will fail.

.. code-block:: python

    t = Table(
        "foo",
        meta,
        Column("bar", String),
        Column("baz", String),
        info={
            "audit.options": {
                "enabled": True,
                "session_settings": [
                    Column("username", String, nullable=False),
                    Column("app_uuid", UUID),
                ],
            }
        },
    )

With all of that set up, we can now create a connection to the database, create the tables, and install the audit triggers!

.. code-block:: python

    url = URL(
        drivername="postgresql+psycopg2",
        host="localhost",
        port=5432,
        password="postgres",
        username="postgres",
    )

    engine = create_engine(url)
    engine.echo = True
    meta.bind = engine

    meta.create_all()
    sqlalchemy_postgresql_audit.install_audit_triggers(meta)
