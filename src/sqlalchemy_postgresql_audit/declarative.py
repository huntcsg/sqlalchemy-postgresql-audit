import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, text

try:
    from sqlalchemy.orm.decl_api import DeclarativeMeta
except ImportError:
    from sqlalchemy.ext.declarative.api import DeclarativeMeta

from sqlalchemy_postgresql_audit.event_listeners.sqlalchemy import (
    create_audit_table as create_raw_audit_table,
)


default_primary_key = Column(
    "audit_pk",
    UUID(as_uuid=True),
    primary_key=True,
    default=uuid.uuid4,
    server_default=text("uuid_generate_v4()"),
)


def audit_model(_func=None, *, enabled=True, primary_key=default_primary_key, **spec):
    """Decorate a model to automatically enable audit modeling.

    Arguments:
        enabled: Defaults to true, enables auditing.
        primary_key: Default to a uuid primary key. Can be disabled by using `None`.

    By default, automatically enables the auditing in addition to hooking
    up the actual audit machinery.

    Additionally, leaves a reference to the audit model's own sqlachemy model
    on the ``__audit_cls__`` attribute of the decorated class.

    Examples:
        >>> from sqlalchemy import Column, types
        >>> from sqlalchemy.ext.declarative import declarative_base
        >>> from sqlalchemy_postgresql_audit import audit_model

        >>> Base = declarative_base()

        >>> @audit_model
        ... class Foo(Base):
        ...     __tablename__ = 'foo'
        ...     id = Column(types.Integer(), primary_key=True)

        >>> Foo.__audit_cls__
        <class '...FooAudit'>

        >>> @audit_model(enabled=False)
        ... class Bar(Base):
        ...     __tablename__ = 'bar'
        ...     id = Column(types.Integer(), primary_key=True)
    """

    def decorated(model_cls):
        model = create_audit_model(
            model_cls, enabled=enabled, primary_key=primary_key, **spec
        )
        if model:
            model_cls.__audit_cls__ = model

        return model_cls

    if _func is None:
        return decorated
    return decorated(_func)


def create_audit_model(
    model_cls, *, enabled=True, primary_key=default_primary_key, **spec
):
    """Create an SQLAlchemy declarative Model class for the given `model_cls`.

    Arguments:
        model_cls: The SQLAlchemy model being audited
        enabled: Defaults to true, enables auditing.
        primary_key: Default to a uuid primary key. Can be disabled by using `None`.

    Examples:
        >>> from sqlalchemy import Column, types
        >>> from sqlalchemy.ext.declarative import declarative_base
        >>> from sqlalchemy_postgresql_audit import create_audit_model

        >>> Base = declarative_base()

        >>> class Foo(Base):
        ...     __tablename__ = 'foo'
        ...     id = Column(types.Integer(), primary_key=True)

        >>> class Bar(Base):
        ...     __tablename__ = 'bar'
        ...     id = Column(types.Integer(), primary_key=True)

        >>> class Baz(Base):
        ...     __tablename__ = 'baz'
        ...     id = Column(types.Integer(), primary_key=True)

        >>> AuditModel = create_audit_model(Foo)
        >>> AuditModel3 = create_audit_model(Baz, primary_key=default_primary_key)
        >>> create_audit_model(Bar, enabled=False)
    """
    base_table = model_cls.__table__
    metadata = model_cls.metadata

    table = create_audit_table(
        base_table, metadata, enabled=enabled, primary_key=primary_key, **spec
    )
    if table is None:
        return

    model_base = _find_model_base(model_cls)

    cls = type(
        "{model_cls}Audit".format(model_cls=model_cls.__name__),
        (model_base,),
        {"__table__": table},
    )

    return cls


def create_audit_table(
    table,
    metadata,
    *,
    enabled=True,
    primary_key=default_primary_key,
    ignore_columns=(),
    **spec
):
    """Create an audit SQLAlchemy ``Table`` for a given `Table` instance.

    Arguments:
        table: The SQLAlchemy `Table` to audit.
        metadata: The `SQLAlchemy` metadata on which to attach the table.
        enabled: Defaults to true, enables auditing.
        primary_key: Default to a uuid primary key. Can be disabled by using `None`.
        spec: Optional auditing spec options.

    Examples:
        >>> from sqlalchemy import MetaData, Table
        >>> from sqlalchemy_postgresql_audit import create_audit_table

        >>> meta = MetaData()

        >>> foo_table = Table('foo', meta)
        >>> audit_table1 = create_audit_table(foo_table, meta)

        >>> baz_table = Table('baz', meta)
        >>> audit_table3 = create_audit_table(baz_table, meta, primary_key=None)

        >>> bar_table = Table('bar', meta)
        >>> create_audit_table(bar_table, meta, enabled=False)
    """
    existing_info = table.info
    existing_info["audit.options"] = {"enabled": enabled, **spec}

    return create_raw_audit_table(
        table,
        metadata,
        primary_key=primary_key,
        ignore_columns=ignore_columns,
    )


def _find_model_base(model_cls):
    for cls in model_cls.__mro__:
        if isinstance(cls, DeclarativeMeta) and not hasattr(cls, "__mapper__"):
            return cls

    raise ValueError("Invalid model, does not subclass a `DeclarativeMeta`.")
