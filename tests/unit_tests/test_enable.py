from sqlalchemy import Table, event


def test_install_event_listeners():
    from sqlalchemy_postgresql_audit.event_listeners import enable_event_listeners
    from sqlalchemy_postgresql_audit.event_listeners.sqlalchemy import (
        create_audit_table,
    )

    assert not event.contains(Table, "after_parent_attach", create_audit_table)

    enable_event_listeners()

    assert event.contains(Table, "after_parent_attach", create_audit_table)
