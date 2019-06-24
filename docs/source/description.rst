Description
-----------

Enables table change tracking support for tables defined by SQLAlchemy models.

Additionally, provides a flexible mechanism for enriching table change data with additional metadata (such as a request UUID or a username or ID).

After registering the relevant SQLAlchemy event listeners, whenever a table is attached to a metadata object, it's info will be checked for specific keys indicating that the table should be audited. If so, a table similar to the source table will be created, with the same name and types (but no constraints or nullability requirements). Additionally, an operation indicator (I, U, D for insert, update, delete), DB timestamp, and `current_user` will be included as columns.

A function and trigger definition are then also defined to insert a row into the audit table whenever a row is inserted, updated, or deleted. For inserts and updates, the row in the audit table is the NEW row representation. For deletes, the row in the audit table is the OLD row.

While any typical create_all/drop_all command will create/drop the relevant tables, Audit Tables info dictionary also contains the DDL necessary to create and drop the function and trigger, and any migration mechanism in usage would need to take advantage of this DDL how it sees fit.

In order to enrich the change data with relevant metadata (such as an application user id or a webrequest UUID, etc), the procedure can be configured (via the table info) to reference any number of session local variables. These variables will be written in the `audit.*` namespace.  Helper functions are provided for setting these these session variables, and it is recommended that you integrate these deeply in your sessionmaking logic.

This library has experimental alembic integration that installs the relevant triggers and functions.  Downgrade support is limited at this time.