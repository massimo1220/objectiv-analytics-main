# Configuration Options
All configuration options are set through environment variables.

## 1. Input Configuration

There is currently one variable supported for configuring the data input format:

- `SCHEMA_EXTENSION_DIRECTORY` - A directory with schema extension files. Each schema extension is a json file that described part
of the full schema. **TODO:** link to a schema explanation.
If not set the default schema is used.

- `SCHEMA_VALIDATION_ERROR_REPORTING` - if set to `true`, after validation, the collector response will
include extensive error reporting as to why certain events have been invalidated.

## 2. Output Configuration
Currently, the only supported non-experimental output option for the collector is Postgres.

Postgres variables:
- `POSTGRES_HOSTNAME`      - Default: `localhost`
- `POSTGRES_PORT`          - Default: `5432`
- `POSTGRES_DB`             - Default: `objectiv`
- `POSTGRES_USER`          - Default: `objectiv`
- `POSTGRES_PASSWORD`       - Needs to be set, as there's no default

## Experimental Configuration Options
There are some additional experimental configuration options. These are not (yet) supported and might be
subject to change in the future. See `config.py` if you wish to use those.
