.. _alembic-integration:

Alembic Integration
-------------------

Alembic is supported through one of two mechanisms:

1. Create your engine with the `audit` plugin enabled

    **`plugins` kwarg**

    .. code-block:: python

        from sqlalchemy import create_engine

        engine = create_engine(
            "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres",
            plugins=['audit'],
        )

    **Via the connection String**

    .. code-block:: python

        from sqlalchemy import create_engine

        engine = create_engine(
            "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres?plugin=audit"
        )

2. Calling :func:`sqlalchemy_postgresql_audit.enable`
