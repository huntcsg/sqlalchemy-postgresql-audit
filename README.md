# SQLAlchemy Postgresql Audit

[![CircleCI](https://circleci.com/gh/huntcsg/sqlalchemy-postgresql-audit.svg?style=svg)](https://circleci.com/gh/huntcsg/sqlalchemy-postgresql-audit) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/a80daeed20654e7aa85358d8e9c761cf)](https://www.codacy.com/app/fool.of.god/sqlalchemy-postgresql-audit?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=huntcsg/sqlalchemy-postgresql-audit&amp;utm_campaign=Badge_Grade) [![codecov](https://codecov.io/gh/huntcsg/sqlalchemy-postgresql-audit/branch/master/graph/badge.svg)](https://codecov.io/gh/huntcsg/sqlalchemy-postgresql-audit) [![Documentation Status](https://readthedocs.org/projects/sqlalchemy-postgresql-audit/badge/?version=latest)](https://sqlalchemy-postgresql-audit.readthedocs.io/en/latest/?badge=latest)


## Description

Enables table change tracking support for tables defined by SQLAlchemy models.

Additionally, provides a flexible mechanism for enriching table change data with additional metadata (such as a request UUID or a username or ID).


## Installation

```bash
pip install sqlalchemy-postgresql-audit
```

This is only known to be compatible with the `postgresql+psycopg2` dialect.

## Usage

See [Docs](https://sqlalchemy-postgresql-audit.readthedocs.io/en/latest/)
