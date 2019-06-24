from sqlalchemy.engine import CreateEnginePlugin
from sqlalchemy.dialects.postgresql.base import PGDialect
from sqlalchemy_postgresql_audit.dialect import PGAdvancedInspector
from sqlalchemy_postgresql_audit.event_listeners import enable_event_listeners


def enable():
    """Enable the advanced inspector and enables sqlalchemy and alembic event listeners."""
    PGDialect.inspector = PGAdvancedInspector
    enable_event_listeners()


class AuditPlugin(CreateEnginePlugin):
    def __init__(self, url, kwargs):
        super(AuditPlugin, self).__init__(url, kwargs)
        enable()
