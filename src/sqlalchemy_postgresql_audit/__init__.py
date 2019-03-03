__version__ = "0.1.1"

import textwrap

from sqlalchemy import DDL, Column, DateTime, Integer, MetaData, String, Table, event

DEFAULT_AUDIT_TABLE_NAMING_CONVENTION = "%(table_name)s_audit"
DEFAULT_AUDIT_TABLE_FUNCTION_NAMING_CONVENTION = "%(schema)s_%(table_name)s_audit"
DEFAULT_AUDIT_TABLE_TRIGGER_CONVENTION = "%(schema)s_%(table_name)s_audit"


def get_audit_spec(table):
    audit_spec = table.info.get("audit.options", {"enabled": False})

    audit_spec["schema"] = audit_spec.get("schema_name", table.schema)
    audit_spec["session_settings"] = audit_spec.get("session_settings", [])

    return audit_spec


def get_create_trigger_ddl(
    function_name,
    trigger_name,
    table_full_name,
    audit_table_full_name,
    session_settings=None,
):
    session_settings = session_settings or []

    deletion_elements = ["'D'", "now()"]

    updation_elements = ["'U'", "now()"]

    insertion_elements = ["'I'", "now()"]

    for session_setting in session_settings:
        type_str = session_setting.type.compile()
        session_settings_element = "current_setting('audit.{}', {})::{}".format(
            session_setting.name,
            "true" if session_setting.nullable else "false",
            type_str,
        )

        deletion_elements.append(session_settings_element)
        updation_elements.append(session_settings_element)
        insertion_elements.append(session_settings_element)

    deletion_elements.append("OLD.*")
    updation_elements.append("NEW.*")
    insertion_elements.append("NEW.*")

    deletion_elements_str = ", ".join(deletion_elements)
    updation_elements_str = ", ".join(updation_elements)
    insertion_elements_str = ", ".join(insertion_elements)

    audit_procedure_ddl = DDL(
        textwrap.dedent(
            """\
            CREATE OR REPLACE FUNCTION {audit_function_name}() RETURNS TRIGGER AS ${trigger_name}$
            BEGIN
                IF (TG_OP = 'DELETE') THEN
                    INSERT INTO {audit_table_full_name} SELECT {deletion_elements};
                ELSIF (TG_OP = 'UPDATE') THEN
                    INSERT INTO {audit_table_full_name} SELECT {updation_elements};
                ELSIF (TG_OP = 'INSERT') THEN
                    INSERT INTO {audit_table_full_name} SELECT {insertion_elements};
                END IF;
                RETURN NULL; -- result is ignored since this is an AFTER trigger
            END;
            ${trigger_name}$ LANGUAGE plpgsql;

            DROP TRIGGER IF EXISTS {trigger_name} ON {table_full_name};

            CREATE TRIGGER {trigger_name}
            AFTER INSERT OR UPDATE OR DELETE ON {table_full_name}
            FOR EACH ROW EXECUTE PROCEDURE {audit_function_name}();
            """
        ).format(
            deletion_elements=deletion_elements_str,
            updation_elements=updation_elements_str,
            insertion_elements=insertion_elements_str,
            table_full_name=table_full_name,
            audit_table_full_name=audit_table_full_name,
            audit_function_name=function_name,
            trigger_name=trigger_name,
        )
    )
    return audit_procedure_ddl


def get_drop_trigger_ddl(function_name, trigger_name, table_full_name):
    return DDL(
        textwrap.dedent(
            """\
            DROP TRIGGER IF EXISTS {trigger_name} ON {table_full_name};
            DROP FUNCTION IF EXISTS {function_name};
            """.format(
                function_name=function_name,
                trigger_name=trigger_name,
                table_full_name=table_full_name,
            )
        )
    )


def install_audit_triggers(metadata, engine=None):
    audit_table_ddl = [
        t.info["audit.create_ddl"]
        for t in metadata.tables.values()
        if t.info.get("audit.is_audit_table")
    ]

    engine = engine or metadata.bind

    if engine:
        for ddl in audit_table_ddl:
            engine.execute(ddl)
    else:
        return audit_table_ddl


def uninstall_audit_triggers(metadata, engine=None):
    audit_table_ddl = [
        t.info["audit.drop_ddl"]
        for t in metadata.tables.values()
        if t.info.get("audit.is_audit_table")
    ]

    engine = engine or metadata.bind

    if engine:
        for ddl in audit_table_ddl:
            engine.execute(ddl)
    else:
        return audit_table_ddl


def set_session_var_stmt(**kwargs):
    format_str = "set local {} = {}"
    stmts = []
    for key, value in kwargs.items():
        stmts.append(format_str.format('"audit.{}"'.format(key), "'{}'".format(value)))
    return "; ".join(stmts) + ";"


def set_session_vars(engine, **kwargs):
    engine.execute(set_session_var_stmt(**kwargs))
