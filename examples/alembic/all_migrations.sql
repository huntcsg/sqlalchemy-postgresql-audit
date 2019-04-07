BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 1992be99c9ec

CREATE TABLE public.test (
    id SERIAL NOT NULL, 
    name VARCHAR NOT NULL, 
    PRIMARY KEY (id)
);

INSERT INTO alembic_version (version_num) VALUES ('1992be99c9ec');

-- Running upgrade 1992be99c9ec -> c03c47b79258

CREATE TABLE public.test_audit (
    audit_operation VARCHAR(1) NOT NULL, 
    audit_operation_timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    id INTEGER, 
    name VARCHAR
);

CREATE OR REPLACE FUNCTION public_test_audit() RETURNS TRIGGER AS $public_test_audit$
BEGIN
    

    IF (TG_OP = 'DELETE') THEN
        INSERT INTO public.test_audit (audit_operation, audit_operation_timestamp, id, name) SELECT 'D', now(), OLD.id, OLD.name;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO public.test_audit (audit_operation, audit_operation_timestamp, id, name) SELECT 'U', now(), NEW.id, NEW.name;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO public.test_audit (audit_operation, audit_operation_timestamp, id, name) SELECT 'I', now(), NEW.id, NEW.name;
    END IF;
    RETURN NULL; -- result is ignored since this is an AFTER trigger
END;
$public_test_audit$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS public_test_audit ON public.test;

CREATE TRIGGER public_test_audit
AFTER INSERT OR UPDATE OR DELETE ON public.test
FOR EACH ROW EXECUTE PROCEDURE public_test_audit();;

UPDATE alembic_version SET version_num='c03c47b79258' WHERE alembic_version.version_num = '1992be99c9ec';

-- Running upgrade c03c47b79258 -> db98d3a3b0f0

ALTER TABLE test ADD COLUMN external_id INTEGER NOT NULL;

ALTER TABLE test_audit ADD COLUMN external_id INTEGER;

CREATE OR REPLACE FUNCTION public_test_audit() RETURNS TRIGGER AS $public_test_audit$
BEGIN
    

    IF (TG_OP = 'DELETE') THEN
        INSERT INTO public.test_audit (audit_operation, audit_operation_timestamp, id, name, external_id) SELECT 'D', now(), OLD.id, OLD.name, OLD.external_id;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO public.test_audit (audit_operation, audit_operation_timestamp, id, name, external_id) SELECT 'U', now(), NEW.id, NEW.name, NEW.external_id;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO public.test_audit (audit_operation, audit_operation_timestamp, id, name, external_id) SELECT 'I', now(), NEW.id, NEW.name, NEW.external_id;
    END IF;
    RETURN NULL; -- result is ignored since this is an AFTER trigger
END;
$public_test_audit$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS public_test_audit ON public.test;

CREATE TRIGGER public_test_audit
AFTER INSERT OR UPDATE OR DELETE ON public.test
FOR EACH ROW EXECUTE PROCEDURE public_test_audit();;

UPDATE alembic_version SET version_num='db98d3a3b0f0' WHERE alembic_version.version_num = 'c03c47b79258';

-- Running upgrade db98d3a3b0f0 -> b010a9200080

ALTER TABLE test_audit ADD COLUMN audit_username VARCHAR NOT NULL;

CREATE OR REPLACE FUNCTION public_test_audit() RETURNS TRIGGER AS $public_test_audit$
BEGIN
    IF current_setting('audit.username', false)::VARCHAR::VARCHAR = '' THEN RAISE EXCEPTION 'audit.username session setting must be set to a non null/empty value'; END IF;

    IF (TG_OP = 'DELETE') THEN
        INSERT INTO public.test_audit (audit_operation, audit_operation_timestamp, audit_username, id, name, external_id) SELECT 'D', now(), current_setting('audit.username', false)::VARCHAR, OLD.id, OLD.name, OLD.external_id;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO public.test_audit (audit_operation, audit_operation_timestamp, audit_username, id, name, external_id) SELECT 'U', now(), current_setting('audit.username', false)::VARCHAR, NEW.id, NEW.name, NEW.external_id;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO public.test_audit (audit_operation, audit_operation_timestamp, audit_username, id, name, external_id) SELECT 'I', now(), current_setting('audit.username', false)::VARCHAR, NEW.id, NEW.name, NEW.external_id;
    END IF;
    RETURN NULL; -- result is ignored since this is an AFTER trigger
END;
$public_test_audit$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS public_test_audit ON public.test;

CREATE TRIGGER public_test_audit
AFTER INSERT OR UPDATE OR DELETE ON public.test
FOR EACH ROW EXECUTE PROCEDURE public_test_audit();;

UPDATE alembic_version SET version_num='b010a9200080' WHERE alembic_version.version_num = 'db98d3a3b0f0';

COMMIT;

