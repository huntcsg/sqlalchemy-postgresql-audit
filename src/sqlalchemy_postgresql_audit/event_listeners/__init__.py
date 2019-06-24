import threading

from sqlalchemy import Table
from sqlalchemy.events import event

_event_listeners_enabled = False


def enable_event_listeners():
    global _event_listeners_enabled

    with threading.Lock():
        if not _event_listeners_enabled:
            _enable_sqlalchemy_event_listeners()
            _enable_alembic_event_listeners()
            _event_listeners_enabled = True


def _enable_sqlalchemy_event_listeners():
    from sqlalchemy_postgresql_audit.event_listeners.sqlalchemy import (
        create_audit_table,
    )

    event.listens_for(Table, "after_parent_attach")(create_audit_table)


def _enable_alembic_event_listeners():
    try:
        from sqlalchemy_postgresql_audit.event_listeners.alembic import (
            compare_for_table,
        )
        from alembic.autogenerate.compare import comparators

        comparators.dispatch_for("table")(compare_for_table)
    except ImportError:
        pass
