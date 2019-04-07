from sqlalchemy.dialects.postgresql.base import PGDialect
from sqlalchemy.engine import CreateEnginePlugin

from sqlalchemy_postgresql_audit.dialect import PGAdvancedInspector


class AuditPlugin(CreateEnginePlugin):
    def __init__(self, url, kwargs):
        super(AuditPlugin, self).__init__(url, kwargs)
        self.install_advanced_inspector()
        self.install_event_listeners()

    def install_advanced_inspector(self):
        PGDialect.inspector = PGAdvancedInspector

    def install_event_listeners(self):
        import sqlalchemy_postgresql_audit.event_listeners.sqlalchemy


# If we are in an alembic context, then this plugin will include some alembic components
# Otherwise we don't care.
try:
    from alembic.autogenerate.compare import comparators
    from alembic.operations.ops import ExecuteSQLOp

    class ReversableExecute(ExecuteSQLOp):
        def __init__(self, sqltext, reverse_ddl, execution_options=None):
            super(ReversableExecute, self).__init__(sqltext, execution_options)
            self._reverse_ddl = reverse_ddl
            self._execution_options = execution_options

        def reverse(self):
            return ExecuteSQLOp(self._reverse_ddl, self._execution_options)

    @comparators.dispatch_for("table")
    def compare_for_table(
        autogen_context, modify_table_ops, schema, tname, conn_table, metadata_table
    ):
        if metadata_table.info.get("audit.is_audit_table"):
            # Case when the audit table is new
            if conn_table is None:
                modify_table_ops.ops.append(
                    ReversableExecute(
                        sqltext=metadata_table.info["audit.create_ddl"],
                        reverse_ddl=metadata_table.info[
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
                            sqltext=str(metadata_table.info["audit.create_ddl"]),
                            reverse_ddl=metadata_table.info[
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


except ImportError:
    pass
