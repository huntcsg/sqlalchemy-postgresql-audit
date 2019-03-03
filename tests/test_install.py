from sqlalchemy import Table, event
from sqlalchemy_postgresql_audit.event_listeners.sqlalchemy import create_audit_table


def test_install_event_listeners(event_listeners):
    assert event.contains(Table, "after_parent_attach", create_audit_table)


def test_event_listener_not_installed_on_import():
    import sqlalchemy_postgresql_audit.event_listeners.sqlalchemy

    assert not event.contains(Table, "after_parent_attach", create_audit_table)
