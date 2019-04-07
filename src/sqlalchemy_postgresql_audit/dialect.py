from sqlalchemy.dialects.postgresql.base import PGInspector

DEFAULT_AUDIT_TABLE_NAMING_CONVENTION = "%(table_name)s_audit"
DEFAULT_AUDIT_TABLE_FUNCTION_NAMING_CONVENTION = "%(schema)s_%(table_name)s_audit"
DEFAULT_AUDIT_TABLE_TRIGGER_CONVENTION = "%(schema)s_%(table_name)s_audit"


class PGAdvancedInspector(PGInspector):
    def reflecttable(self, table, include_columns, **kwargs):
        super(PGAdvancedInspector, self).reflecttable(table, include_columns, **kwargs)
        # TODO: Retrieve trigger/procedure information for the particular table.
