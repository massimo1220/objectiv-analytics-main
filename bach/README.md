# Objectiv Bach: Pandas-like DataFrames backed by SQL

Bach is a python-based data modeling library that enables you to use Pandas-like operations that run on your full dataset in the SQL database. Any dataframe or model built with Bach can be converted to an SQL statement with a single command. It includes a set of operations that enable effective feature creation for data sets that embrace the [open analytics taxonomy](https://objectiv.io/docs/taxonomy/).

Bach uses [`sql_models`](./sql_models/) under the hood, which makes it possible to easily build graphs of SQL models and generate SQL for the resulting composite `sql-models`. See [sql_models/README.md](./sql_models/README.md) for more information.

Visit [Objectiv Docs](https://objectiv.io/docs/modeling/bach/) to learn more

## Using Bach
To use Bach, use the following command:
```bash
pip install objectiv-bach
pip install objectiv-bach[bigquery] # for bigquery support
```

If you want the latest and greatest from your local checkout, install objectiv_bach in edit mode:
```bash
pip install -e .
pip install -e .[bigquery] # for bigquery support
```

This will install Bach in edit mode, meaning you get the latest version from the local checkout.
For detailed installation & usage instructions, visit [Objectiv Docs](https://www.objectiv.io/docs).


## Running Functional and Unit Tests
In case you are interested on running tests, install all dev requirements through:
```bash
pip install -e .[dev,bigquery]
```

### Setting up environmental variables
Functional tests require access to multiple databases. In order to run them you should define
the variables shown in the below table, depending on the engine you want to test.
Variables can be set as environment variables, or can be defined in the file `.secrets/.test_env`.

| Database | Variables                              | Description                  |
|:--------:|----------------------------------------|------------------------------|
| Postgres | `OBJ_DB_PG_TEST_URL`                   | Database URL                 |
|          |                                        |                              |
|  Athena  | `OBJ_DB_ATHENA_TEST_URL`               | Database URL                 |
|  Athena  | `OBJ_DB_ATHENA_AWS_ACCESS_KEY_ID`      | Access key id*               |
|  Athena  | `OBJ_DB_ATHENA_AWS_SECRET_ACCESS_KEY`  | Secret key*                  |
|  Athena  | `OBJ_DB_ATHENA_REGION_NAME`            | Region*                      |
|  Athena  | `OBJ_DB_ATHENA_SCHEMA_NAME`            | Schema name*                 |
|  Athena  | `OBJ_DB_ATHENA_S3_STAGING_DIR`         | S3 staging dir*              |
|  Athena  | `OBJ_DB_ATHENA_WORK_GROUP`             | Workgroup to run queries as* |
|          |                                        |                              |
| BigQuery | `OBJ_DB_BQ_TEST_URL`                   | Database URL                 |
| BigQuery | `OBJ_DB_BQ_CREDENTIALS_PATH`           | Credentials Path             |

For Athena one can either specify the full connection string as `OBJ_DB_ATHENA_TEST_URL` or set
all the fields marked with an asterisk. The asterisk marked fields are ignored if `OBJ_DB_ATHENA_TEST_URL`
is set.

For more information on creating the correct database setup, see the markdown files in the `tests/` folder.


### Running Tests for different databases
For running tests for Postgres, as well as database independent tests, run the following command:
```bash
make tests
```

For running tests for Athena, as well as database independent tests, run the following command:
```bash
make tests-athena
```

For running tests for BigQuery, as well as database independent tests, run the following command:
```bash
make tests-bigquery
```

In case you want to run all tests for all supported databases, as well as database independent tests, run
the following command:
```bash
make tests-all
```

## See Also
* [Pandas](https://github.com/pandas-dev/pandas): the inspiration for the API.
   Pandas has excellent [documentation](https://pandas.pydata.org/docs/) for its API.
* [SQL-models](./sql_models/): Sub-project that is used for generating the underlying sql-queries. Can be 
  found in the [`sql_models`](./sql_models/) package

## Support & Troubleshooting
If you need help using or installing Bach, join our [Slack channel](https://objectiv.io/join-slack/) and post your question there. 

## Bug Reports & Feature Requests
If you’ve found an issue or have a feature request, please check out the [Contribution Guide](https://objectiv.io/docs/home/the-project/contribute/).

## Security Disclosure
Found a security issue? Please don’t use the issue tracker but contact us directly. See [SECURITY.md](../SECURITY.md) for details.

## Custom development & contributing code
If you want to contribute to Objectiv or use it as a base for custom development, take a look at [CONTRIBUTING.md](CONTRIBUTING.md). It contains detailed development instructions and a link to information about our contribution process and where you can fit in.

## License
This repository is part of the source code for Objectiv, which is released under the Apache 2.0 License. Please refer to [LICENSE.md](../LICENSE.md) for details.
