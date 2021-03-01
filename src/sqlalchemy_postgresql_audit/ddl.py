from sqlalchemy.dialects.postgresql.base import RESERVED_WORDS

from .templates import make_audit_procedure, make_drop_audit_procedure


def get_audit_spec(table):
    audit_spec = table.info.get("audit.options", {"enabled": False})

    audit_spec["schema"] = audit_spec.get("schema_name", table.schema)
    audit_spec["session_settings"] = audit_spec.get("session_settings", [])

    return audit_spec


def get_create_trigger_ddl(
    target_columns,
    audit_columns,
    function_name,
    trigger_name,
    table_full_name,
    audit_table_full_name,
    session_settings=None,
):
    session_settings = session_settings or []

    deletion_elements = ["'D'", "now()", "current_user"]

    updation_elements = ["'U'", "now()", "current_user"]

    insertion_elements = ["'I'", "now()", "current_user"]

    setting_map = {
        session_setting.name: session_setting for session_setting in session_settings
    }

    column_elements = []
    check_settings = []

    for col in audit_columns.values():
        column_name = (
            '"{}"'.format(col.name)
            if (col.name.lower() in RESERVED_WORDS or col.name.lower() != col.name)
            else col.name
        )

        # We need to make sure to explicitly reference all elements in the procedure
        column_elements.append(column_name)

        # If this value is coming out of the target, then we want to explicitly reference the value
        if col.name in target_columns:
            deletion_elements.append("OLD.{}".format(column_name))
            updation_elements.append("NEW.{}".format(column_name))
            insertion_elements.append("NEW.{}".format(column_name))

        # If it is not, it is either a default "audit_*" column
        # or it is one of our session settings values
        else:
            if col.name in (
                "audit_operation",
                "audit_operation_timestamp",
                "audit_current_user",
            ):
                continue

            session_setting = setting_map[col.name]
            type_str = session_setting.type.compile()
            name = session_setting.name.split("audit_", 1)[-1]

            session_settings_element = "current_setting('audit.{}', {})::{}".format(
                name, "true" if session_setting.nullable else "false", type_str
            )
            deletion_elements.append(session_settings_element)
            updation_elements.append(session_settings_element)
            insertion_elements.append(session_settings_element)

            # This handles a kind of strange behavior where if you set a session setting
            # and then commit the transaction you will end up with an empty string in that setting
            # and then the procedure will succeed, despite the value being "empty".
            if not session_setting.nullable:
                check_settings.append(
                    "IF {}::VARCHAR = '' THEN RAISE EXCEPTION "
                    "'audit.{} session setting must be set to a non null/empty value'; "
                    "END IF;".format(session_settings_element, name)
                )

    return make_audit_procedure(
        audit_table_full_name=audit_table_full_name,
        table_full_name=table_full_name,
        procedure_name=function_name,
        trigger_name=trigger_name,
        deletion_elements=deletion_elements,
        updation_elements=updation_elements,
        insertion_elements=insertion_elements,
        audit_columns=column_elements,
        check_settings=check_settings,
    )


def get_drop_trigger_ddl(function_name, trigger_name, table_full_name):
    return make_drop_audit_procedure(function_name, trigger_name, table_full_name)


def install_audit_triggers(metadata, engine=None):
    """Installs all audit triggers.

    This can be used after calling `metadata.create_all()` to create
    all the procedures and triggers.

    :param metadata: A :class:`sqlalchemy.sql.schema.MetaData`
    :param engine: A :class:`sqlalchemy.engine.Engine` or None
    :return: None or a :class:`str` for the DDL needed to install all audit triggers.
    """
    audit_table_ddl = [
        t.info["audit.create_ddl"]
        for t in metadata.tables.values()
        if t.info.get("audit.is_audited")
    ]

    engine = engine or metadata.bind

    if engine:
        for ddl in audit_table_ddl:
            engine.execute(ddl)
    else:
        return "; ".join(audit_table_ddl)


def uninstall_audit_triggers(metadata, engine=None):
    """Uninstalls all audit triggers.

    This can be used to remove all audit triggers.

    :param metadata: A :class:`sqlalchemy.sql.schema.MetaData`
    :param engine: A :class:`sqlalchemy.engine.Engine` or None
    :return: None or a :class:`str` for the DDL needed to uninstall all audit triggers.
    """
    audit_table_ddl = [
        t.info["audit.drop_ddl"]
        for t in metadata.tables.values()
        if t.info.get("audit.is_audited")
    ]

    engine = engine or metadata.bind

    if engine:
        for ddl in audit_table_ddl:
            engine.execute(ddl)
    else:
        return ";\n ".join(audit_table_ddl)
