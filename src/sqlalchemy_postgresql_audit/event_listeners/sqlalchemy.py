from sqlalchemy import Column, DateTime, String, Table
from sqlalchemy.events import event

from sqlalchemy_postgresql_audit.ddl import (
    get_audit_spec,
    get_create_trigger_ddl,
    get_drop_trigger_ddl,
)
from sqlalchemy_postgresql_audit.dialect import (
    DEFAULT_AUDIT_TABLE_FUNCTION_NAMING_CONVENTION,
    DEFAULT_AUDIT_TABLE_NAMING_CONVENTION,
    DEFAULT_AUDIT_TABLE_TRIGGER_CONVENTION,
)


@event.listens_for(Table, "after_parent_attach")
def create_audit_table(target, parent):
    audit_spec = get_audit_spec(target)

    if not audit_spec.get("enabled"):
        return

    if target.schema is None:
        raise ValueError(
            "A table must have a schema name in order to have an audit table created"
        )

    audit_table_naming_convention = parent.naming_convention.get(
        "audit.table", DEFAULT_AUDIT_TABLE_NAMING_CONVENTION
    )
    audit_function_naming_convention = parent.naming_convention.get(
        "audit.function", DEFAULT_AUDIT_TABLE_FUNCTION_NAMING_CONVENTION
    )
    audit_trigger_naming_convention = parent.naming_convention.get(
        "audit.trigger", DEFAULT_AUDIT_TABLE_TRIGGER_CONVENTION
    )

    audit_table_name = audit_table_naming_convention % {
        "table_name": target.name,
        "schema": audit_spec["schema"],
    }
    audit_function_name = audit_function_naming_convention % {
        "table_name": target.name,
        "schema": audit_spec["schema"],
    }
    audit_trigger_name = audit_trigger_naming_convention % {
        "table_name": target.name,
        "schema": audit_spec["schema"],
    }

    columns = [
        Column(col.name, col.type, nullable=True) for col in target.columns.values()
    ]
    session_setting_columns = [col.copy() for col in audit_spec["session_settings"]]
    for col in session_setting_columns:
        col.name = "audit_{}".format(col.name)

    column_elements = session_setting_columns + columns

    audit_table = Table(
        audit_table_name,
        target.metadata,
        Column("audit_operation", String(1), nullable=False),
        Column("audit_operation_timestamp", DateTime, nullable=False),
        *column_elements,
        schema=audit_spec["schema"]
    )

    audit_table.info["audit.create_ddl"] = get_create_trigger_ddl(
        target.columns,
        audit_table.columns,
        audit_function_name,
        audit_trigger_name,
        target.fullname,
        audit_table.fullname,
        session_setting_columns,
    )

    audit_table.info["audit.drop_ddl"] = get_drop_trigger_ddl(
        audit_function_name, audit_trigger_name, target.fullname
    )
    audit_table.info["audit.is_audit_table"] = True
    target.info["audit.is_audited"] = True
