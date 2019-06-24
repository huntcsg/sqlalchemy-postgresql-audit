from unittest import TestCase


class TestPackageExports(TestCase):
    def test_session_vars(self):
        from sqlalchemy_postgresql_audit import set_session_vars

    def test_enable(self):
        from sqlalchemy_postgresql_audit import enable

    def test_install_audit_triggers(self):
        from sqlalchemy_postgresql_audit import install_audit_triggers

    def test_uninstall_audit_triggers(self):
        from sqlalchemy_postgresql_audit import uninstall_audit_triggers
