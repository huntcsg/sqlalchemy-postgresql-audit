Getting Started
---------------

1. Install the package (see :ref:`Installation <installation>`)
2. Enable the SQLAlchemy and/or Alembic event listeners and components. It is critical that this happens *prior* to adding any tables you want to audit to the metadata object.

    .. code-block:: python

        from sqlalchemy import MetaData
        import sqlalchemy_postgresql_audit
        
        sqlalchemy_postgresql_audit.enable()

        metadata = MetaData()


3. Add an `audit.options` key to the table `info` attribute.

    **ORM Style**

    .. code-block:: python

        class Base:

            @declared_attr
            def __table_args__(self):
                return {
                    'info': {
                        'audit.options': {
                            'enabled': True,
                        },
                    }
                }

    **Core Style**

    .. code-block:: python

        table = Table(
            "bar",
            metadata,
            Column("foo", String),
            info={
                "audit.options": {
                    "enabled": True
                }
            },
        )

4. Install the triggers and functions from the metadata

    .. code-block:: python

        from sqlalchemy_postgresql_audit import install_audit_triggers

        install_audit_triggers(metadata, engine)
