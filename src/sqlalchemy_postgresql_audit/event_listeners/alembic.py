from alembic.operations.ops import ExecuteSQLOp


class ReversableExecute(ExecuteSQLOp):
    def __init__(self, sqltext, reverse_ddl, execution_options=None):
        super(ReversableExecute, self).__init__(sqltext, execution_options)
        self._reverse_ddl = reverse_ddl
        self._execution_options = execution_options

    def reverse(self):
        return ExecuteSQLOp(self._reverse_ddl, self._execution_options)


def compare_for_table(
    autogen_context, modify_table_ops, schema, tname, conn_table, metadata_table
):
    # Early exit if there is no metadata table or we can't get it's info.
    # This handles alembic version tables, but also others.
    if metadata_table is None or not hasattr(metadata_table, "info"):
        return

    if metadata_table.info.get("audit.is_audit_table"):
        # Case when the audit table is new
        if conn_table is None:
            modify_table_ops.ops.append(
                ReversableExecute(
                    sqltext=metadata_table.info["audit.target_table"].info[
                        "audit.create_ddl"
                    ],
                    reverse_ddl=metadata_table.info["audit.target_table"].info[
                        "audit.drop_ddl"
                    ],  # TODO: Use reflected DDL from the database
                )
            )

        # Case when the audit table exists already
        else:
            existing_audit_table_columns = set(
                [col.name for col in conn_table.columns.values()]
            )
            defined_audit_table_columns = set(
                [col.name for col in metadata_table.columns.values()]
            )

            # Case when the audit table has new columns.
            # TODO: Check if the settings types have changed.
            #  Not 100% sure how this would be done.
            if existing_audit_table_columns.symmetric_difference(
                defined_audit_table_columns
            ):
                modify_table_ops.ops.append(
                    ReversableExecute(
                        sqltext=metadata_table.info["audit.target_table"].info[
                            "audit.create_ddl"
                        ],
                        reverse_ddl=metadata_table.info["audit.target_table"].info[
                            "audit.drop_ddl"
                        ],  # TODO: Use reflected DDL from the database
                    )
                )

            # Case when the audit table triggers _should_ already be installed
            else:
                # TODO: Check to ensure that the triggers are installed
                pass

    elif not metadata_table.info.get("audit.is_audited"):
        # TODO: Drop the triggers if they exist.
        pass
