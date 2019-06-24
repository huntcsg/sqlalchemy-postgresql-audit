import textwrap

PROCEDURE_TEMPLATE = textwrap.dedent(
    """\
    CREATE OR REPLACE FUNCTION {audit_function_name}() RETURNS TRIGGER AS ${trigger_name}$
    BEGIN
        {check_settings}

        IF (TG_OP = 'DELETE') THEN
            INSERT INTO {audit_table_full_name} ({audit_columns}) SELECT {deletion_elements};
        ELSIF (TG_OP = 'UPDATE') THEN
            INSERT INTO {audit_table_full_name} ({audit_columns}) SELECT {updation_elements};
        ELSIF (TG_OP = 'INSERT') THEN
            INSERT INTO {audit_table_full_name} ({audit_columns}) SELECT {insertion_elements};
        END IF;
        RETURN NULL; -- result is ignored since this is an AFTER trigger
    END;
    ${trigger_name}$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS {trigger_name} ON {table_full_name};

    CREATE TRIGGER {trigger_name}
    AFTER INSERT OR UPDATE OR DELETE ON {table_full_name}
    FOR EACH ROW EXECUTE PROCEDURE {audit_function_name}();
    """
)


DROP_PROCEDURE_TEMPLATE = textwrap.dedent(
    """\
    DROP TRIGGER IF EXISTS {trigger_name} ON {table_full_name};
    DROP FUNCTION IF EXISTS {function_name};
    """
)


def make_audit_procedure(
    procedure_name,
    trigger_name,
    check_settings,
    audit_table_full_name,
    table_full_name,
    audit_columns,
    deletion_elements,
    updation_elements,
    insertion_elements,
):
    """Return the string

    :param procedure_name: The name for the procedure
    :param trigger_name:  The name for the trigger
    :param check_settings: A list of settings checks.
        Used to validate that the settings are non-empty.
    :param audit_table_full_name: The full name (including schema) of the audit table
    :param table_full_name: The full name (including schema) of the audited table
    :param audit_columns: A list of columns to be audited
    :param deletion_elements: A list of column expressions
        suitable to use in the VALUES block of an insert statement.
    :param updation_elements: A list of column expressions
        suitable to use in the VALUES block of an insert statement.
    :param insertion_elements: A list of column expressions
        suitable to use in the VALUES block of an insert statement.
    :return: A :class:`str` of the full DDL needed to be executed
        to create the procedure and trigger.
    """

    deletion_elements_str = ", ".join(deletion_elements)
    updation_elements_str = ", ".join(updation_elements)
    insertion_elements_str = ", ".join(insertion_elements)
    columns_str = ", ".join(audit_columns)
    check_settings_str = "\n    ".join(check_settings)

    return PROCEDURE_TEMPLATE.format(
        audit_function_name=procedure_name,
        trigger_name=trigger_name,
        check_settings=check_settings_str,
        audit_table_full_name=audit_table_full_name,
        table_full_name=table_full_name,
        audit_columns=columns_str,
        deletion_elements=deletion_elements_str,
        updation_elements=updation_elements_str,
        insertion_elements=insertion_elements_str,
    )


def make_drop_audit_procedure(function_name, trigger_name, table_full_name):
    return DROP_PROCEDURE_TEMPLATE.format(
        function_name=function_name,
        trigger_name=trigger_name,
        table_full_name=table_full_name,
    )
