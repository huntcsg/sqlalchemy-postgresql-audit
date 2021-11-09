__version__ = "0.5.2"

__all__ = [
    "set_session_vars",
    "enable",
    "install_audit_triggers",
    "uninstall_audit_triggers",
    "audit_model",
    "create_audit_model",
    "create_audit_table",
]

from .declarative import audit_model, create_audit_model, create_audit_table
from .ddl import install_audit_triggers, uninstall_audit_triggers
from .plugin import enable
from .session import set_session_vars
