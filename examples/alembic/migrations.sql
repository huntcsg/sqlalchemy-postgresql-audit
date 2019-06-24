BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 3bf110ac566b

CREATE TABLE test (
    id SERIAL NOT NULL, 
    name VARCHAR NOT NULL, 
    PRIMARY KEY (id)
);

INSERT INTO alembic_version (version_num) VALUES ('3bf110ac566b');

-- Running upgrade 3bf110ac566b -> c1197ef009a5

CREATE TABLE test_audit (
    audit_operation VARCHAR(1) NOT NULL, 
    audit_operation_timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    audit_current_user VARCHAR(64) NOT NULL, 
    id INTEGER, 
    name VARCHAR
);

CREATE OR REPLACE FUNCTION public_test_audit() RETURNS TRIGGER AS $public_test_audit$
BEGIN
    

    IF (TG_OP = 'DELETE') THEN
        INSERT INTO test_audit (audit_operation, audit_operation_timestamp, audit_current_user, id, name) SELECT 'D', now(), current_user, OLD.id, OLD.name;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO test_audit (audit_operation, audit_operation_timestamp, audit_current_user, id, name) SELECT 'U', now(), current_user, NEW.id, NEW.name;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO test_audit (audit_operation, audit_operation_timestamp, audit_current_user, id, name) SELECT 'I', now(), current_user, NEW.id, NEW.name;
    END IF;
    RETURN NULL; -- result is ignored since this is an AFTER trigger
END;
$public_test_audit$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS public_test_audit ON test;

CREATE TRIGGER public_test_audit
AFTER INSERT OR UPDATE OR DELETE ON test
FOR EACH ROW EXECUTE PROCEDURE public_test_audit();;

UPDATE alembic_version SET version_num='c1197ef009a5' WHERE alembic_version.version_num = '3bf110ac566b';

-- Running upgrade c1197ef009a5 -> 33d56e6de360

ALTER TABLE test_audit ADD COLUMN audit_username VARCHAR NOT NULL;

CREATE OR REPLACE FUNCTION public_test_audit() RETURNS TRIGGER AS $public_test_audit$
BEGIN
    IF current_setting('audit.username', false)::VARCHAR::VARCHAR = '' THEN RAISE EXCEPTION 'audit.username session setting must be set to a non null/empty value'; END IF;

    IF (TG_OP = 'DELETE') THEN
        INSERT INTO test_audit (audit_operation, audit_operation_timestamp, audit_current_user, audit_username, id, name) SELECT 'D', now(), current_user, current_setting('audit.username', false)::VARCHAR, OLD.id, OLD.name;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO test_audit (audit_operation, audit_operation_timestamp, audit_current_user, audit_username, id, name) SELECT 'U', now(), current_user, current_setting('audit.username', false)::VARCHAR, NEW.id, NEW.name;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO test_audit (audit_operation, audit_operation_timestamp, audit_current_user, audit_username, id, name) SELECT 'I', now(), current_user, current_setting('audit.username', false)::VARCHAR, NEW.id, NEW.name;
    END IF;
    RETURN NULL; -- result is ignored since this is an AFTER trigger
END;
$public_test_audit$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS public_test_audit ON test;

CREATE TRIGGER public_test_audit
AFTER INSERT OR UPDATE OR DELETE ON test
FOR EACH ROW EXECUTE PROCEDURE public_test_audit();;

UPDATE alembic_version SET version_num='33d56e6de360' WHERE alembic_version.version_num = 'c1197ef009a5';

-- Running upgrade 33d56e6de360 -> 90602f3b86e4

ALTER TABLE test ADD COLUMN external_id INTEGER NOT NULL;

ALTER TABLE test_audit ADD COLUMN external_id INTEGER;

CREATE OR REPLACE FUNCTION public_test_audit() RETURNS TRIGGER AS $public_test_audit$
BEGIN
    IF current_setting('audit.username', false)::VARCHAR::VARCHAR = '' THEN RAISE EXCEPTION 'audit.username session setting must be set to a non null/empty value'; END IF;

    IF (TG_OP = 'DELETE') THEN
        INSERT INTO test_audit (audit_operation, audit_operation_timestamp, audit_current_user, audit_username, id, name, external_id) SELECT 'D', now(), current_user, current_setting('audit.username', false)::VARCHAR, OLD.id, OLD.name, OLD.external_id;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO test_audit (audit_operation, audit_operation_timestamp, audit_current_user, audit_username, id, name, external_id) SELECT 'U', now(), current_user, current_setting('audit.username', false)::VARCHAR, NEW.id, NEW.name, NEW.external_id;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO test_audit (audit_operation, audit_operation_timestamp, audit_current_user, audit_username, id, name, external_id) SELECT 'I', now(), current_user, current_setting('audit.username', false)::VARCHAR, NEW.id, NEW.name, NEW.external_id;
    END IF;
    RETURN NULL; -- result is ignored since this is an AFTER trigger
END;
$public_test_audit$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS public_test_audit ON test;

CREATE TRIGGER public_test_audit
AFTER INSERT OR UPDATE OR DELETE ON test
FOR EACH ROW EXECUTE PROCEDURE public_test_audit();;

UPDATE alembic_version SET version_num='90602f3b86e4' WHERE alembic_version.version_num = '33d56e6de360';

COMMIT;

