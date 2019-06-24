def set_session_var_stmt(**kwargs):
    """Returns proper sql statements for setting session settings.

    Namespaces all settings under `audit.*` namespace.

    e.g.

        .. code-block:: python

            set_session_var_stmt(foo='bar', baz='foobaz')
            # set local "audit.foo" = 'bar'; set local "audit.baz" = 'foobaz';

    :param kwargs: key/value pairs of values to set.
    :return: a :class:`str`, valid to set the relevant settings.
    """
    format_str = "set local {} = {}"
    stmts = []
    for key, value in kwargs.items():
        stmts.append(format_str.format('"audit.{}"'.format(key), "'{}'".format(value)))
    return "; ".join(stmts) + ";"


def set_session_vars(connectable, **kwargs):
    """Wrapper to set session settings.

    This must be set *in* a transaction in order for these settings to be present.

    Typical use cases would be a username coming from a web request, or a request UUID
    or a script name.

    :param connectable: A connectable that we can execute on.
    :param kwargs: key/value pairs of values to set.
    :return: None
    """
    connectable.execute(set_session_var_stmt(**kwargs))
