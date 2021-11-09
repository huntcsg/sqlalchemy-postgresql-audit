from sqlalchemy import Column, Integer, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base

import sqlalchemy_postgresql_audit


def setup():
    sqlalchemy_postgresql_audit.enable()


def test_vanilla_model():
    Base = declarative_base()
    metadata = Base.metadata

    @sqlalchemy_postgresql_audit.audit_model
    class Model(Base):
        __tablename__ = 'foo'

        id = Column("id", Integer, primary_key=True)

    audit_table = metadata.tables["foo_audit"]

    assert audit_table.info["audit.is_audit_table"]
    assert Model.__table__.info["audit.is_audited"]


def test_model_with_info():
    Base = declarative_base()
    metadata = Base.metadata

    @sqlalchemy_postgresql_audit.audit_model
    class Model(Base):
        __tablename__ = 'foo'
        __table_args__ = {
                'info': {'example': 4}
            }

        id = Column("id", Integer, primary_key=True)

    audit_table = metadata.tables["foo_audit"]

    assert audit_table.info["audit.is_audit_table"]
    assert Model.__table__.info["audit.is_audited"]
    assert 'example' in  Model.__table__.info
