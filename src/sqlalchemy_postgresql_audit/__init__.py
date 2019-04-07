__version__ = "0.2.0"


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
        return "; ".join(audit_table_ddl)


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
        return ";\n ".join(audit_table_ddl)


def set_session_var_stmt(**kwargs):
    format_str = "set local {} = {}"
    stmts = []
    for key, value in kwargs.items():
        stmts.append(format_str.format('"audit.{}"'.format(key), "'{}'".format(value)))
    return "; ".join(stmts) + ";"


def set_session_vars(engine, **kwargs):
    engine.execute(set_session_var_stmt(**kwargs))
