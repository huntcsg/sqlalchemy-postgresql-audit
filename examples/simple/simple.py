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
    schema="public",
)

r = Table(
    "bar",
    meta,
    Column("foo", String),
    info={"audit.options": {"enabled": True}},
    schema="public",
)

print("Tables: ", meta.tables)


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
