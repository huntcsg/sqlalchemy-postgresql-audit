def install():
    import sqlalchemy_postgresql_audit.event_listeners.sqlalchemy

    sqlalchemy_postgresql_audit.event_listeners.sqlalchemy.install()


def uninstall():
    import sqlalchemy_postgresql_audit.event_listeners.sqlalchemy

    sqlalchemy_postgresql_audit.event_listeners.sqlalchemy.uninstall()
