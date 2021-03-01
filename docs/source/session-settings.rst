Session Settings
----------------

In order to enrich the audit tables with information, we can set session settings that live for the duration of a transaction.


**SQLAlchemy Session**

.. code-block:: python

    from sqlalchemy_postgresql_audit import set_session_vars
    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(bind=engine)
    session = Session()

    set_session_vars(session, username='huntcsg')
    session.execute(insert_stmt, { ... values ... })
    session.commit()



**SQLAlchemy Connection**

.. code-block:: python

    from sqlalchemy_postgresql_audit import set_session_vars

    with engine.connect() as conn:
        with conn.begin() as trans:
            set_session_vars(conn, username='huntcsg')
            conn.execute(insert_stmt, { ... values ... })


**SQLAlchemy Engine**

.. code-block:: python

    from sqlalchemy_postgresql_audit import set_session_vars
    with engine.begin() as conn:
        set_session_vars(conn, username='huntcsg')
        conn.execute(insert_stmt, { ... values ... })
