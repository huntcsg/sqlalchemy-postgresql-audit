from sqlalchemy import MetaData, Table, Column, Integer
import sqlalchemy_postgresql_audit


def test_audit_table_gets_added():

    sqlalchemy_postgresql_audit.enable()
    metadata = MetaData()
    table = Table(
        "foo",
        metadata,
        Column("bar", Integer),
        info={"audit.options": {"enabled": True}},
    )

    audit_table = metadata.tables["foo_audit"]

    assert audit_table.info["audit.is_audit_table"]
    assert table.info["audit.is_audited"]
