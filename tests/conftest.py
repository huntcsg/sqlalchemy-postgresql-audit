from sqlalchemy_postgresql_audit.event_listeners import install, uninstall
import pytest


@pytest.fixture()
def event_listeners():
    try:
        install()
        yield

    finally:
        uninstall()
