# Instructions

1. Install package and dependencies
    ```bash
    $ pip install sqlalchemy-postgresql-audit
    $ pip install psycopg2
    $ pip install alembic
    $ pip install -e test-app

2. Run

    ```bash
    $ docker-compose up -d

3. Run
    
    ```bash
   $ alembic upgrade head

4. Database now has tables, audit tables, and triggers.
