from sqlalchemy.dialects.postgresql.base import PGInspector

DEFAULT_AUDIT_TABLE_NAMING_CONVENTION = "%(table_name)s_audit"
"""The audit table naming convetion. Change this at naming_conventions `audit.table` key."""

DEFAULT_AUDIT_TABLE_FUNCTION_NAMING_CONVENTION = "%(schema)s_%(table_name)s_audit"
"""The audit table naming convetion. Change this at naming_conventions `audit.table` key."""

DEFAULT_AUDIT_TABLE_TRIGGER_CONVENTION = "%(schema)s_%(table_name)s_audit"
"""The audit table naming convetion. Change this at naming_conventions `audit.table` key."""


class PGAdvancedInspector(PGInspector):
    """A subclass of :class:`sqlalchemy.dialects.postgresql.base.PGInspector`.

    Enables advanced database reflection.
    """

    def reflecttable(self, table, include_columns, *args, **kwargs):
        super(PGAdvancedInspector, self).reflecttable(
            table, include_columns, *args, **kwargs
        )
        # TODO: Retrieve trigger/procedure information for the particular table.
