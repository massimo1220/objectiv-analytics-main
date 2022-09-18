"""
Copyright 2022 Objectiv B.V.

### Fixtures
There is some pytest 'magic' here that automatically fills out the 'engine' and 'dialect' parameters for
test functions that have either of those.
By default such a test function will get a Postgres dialect or engine. But if --big-query, --athena or --all
is specified on the commandline, then it will (also) get a BigQuery/Athena dialect or engine. For specific
tests, it is possible to disable testing for certain databases, see 'marks' section below.

### Marks and Test Categorization
A lot of functionality needs to be tested for multiple databases. The 'engine' and 'dialects' fixtures
mentioned above help with that. Additionally we have some marks (`@pytest.mark.<type>`) to make it explicit
which databases we expect tests to run against.

We broadly want 4 categories of tests:
* unit-test: These don't interact with a database
  * unit-tests that are tested with multiple database dialects (1)
  * unit-tests that are database-dialect independent (2)
* functional-tests: These interact with a database
  *  functional-tests that run against all supported databases (3)
  *  functional-tests that run against all supported databases except some specific databases (4)

1 and 3 are the default for tests. These either get 'engine' or 'dialect' as fixture and run against all
databases. Category 2 are tests that test generic code that is not geared to a specific database.
Category 4 is for functionality that we explicitly not support on some databases.

Category 2 and 4 are the exception, these need to be marked with the `db_independent`, `skip_postgres`,
`skip_bigquery` or `skip_athena` marks.

### Other
For all unittests we add a timeout of 1 second. If they take longer they will be stopped and considered
failed.

The fixture `unique_table_test_name` gives out a unique table name to each test that use it. These tables are
automatically deleted at the end of the test session.
"""
import os
from collections import defaultdict
from enum import Enum
from typing import Dict, List
from urllib.parse import quote_plus

import pytest
from _pytest.fixtures import SubRequest
from _pytest.main import Session
from _pytest.python import Metafunc, Function
from _pytest.config.argparsing import Parser
from dotenv import dotenv_values
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

# Load settings from .test_env file, but allow overrides from Environment variables
_DOT_ENV_FILE = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/.secrets/.test_env'
_ENV = {
    **dotenv_values(_DOT_ENV_FILE),
    **os.environ
}

_DB_PG_TEST_URL = _ENV.get('OBJ_DB_PG_TEST_URL', 'postgresql://objectiv:@localhost:5432/objectiv')
_DB_BQ_TEST_URL = _ENV.get('OBJ_DB_BQ_TEST_URL', 'bigquery://objectiv-snowplow-test-2/bach_test')
_DB_BQ_CREDENTIALS_PATH = _ENV.get(
    'OBJ_DB_BQ_CREDENTIALS_PATH',
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/.secrets/bach-big-query-testing.json'
)
_DB_ATHENA_TEST_URL = _ENV.get('OBJ_DB_ATHENA_TEST_URL')
_DB_ATHENA_AWS_ACCESS_KEY_ID = _ENV.get('OBJ_DB_ATHENA_AWS_ACCESS_KEY_ID')
_DB_ATHENA_AWS_SECRET_ACCESS_KEY = _ENV.get('OBJ_DB_ATHENA_AWS_SECRET_ACCESS_KEY')
_DB_ATHENA_REGION_NAME = _ENV.get('OBJ_DB_ATHENA_REGION_NAME', 'eu-west-1')
_DB_ATHENA_SCHEMA_NAME = _ENV.get('OBJ_DB_ATHENA_SCHEMA_NAME', 'automated_tests.bach_test')
_DB_ATHENA_S3_STAGING_DIR = _ENV.get('OBJ_DB_ATHENA_S3_STAGING_DIR', 's3://obj-automated-tests/bach_test/staging/')
_DB_ATHENA_WORK_GROUP = _ENV.get('OBJ_DB_ATHENA_WORK_GROUP', 'automated_tests_work_group')


MARK_DB_INDEPENDENT = 'db_independent'
MARK_SKIP_POSTGRES = 'skip_postgres'
MARK_SKIP_ATHENA = 'skip_athena'
MARK_SKIP_BIGQUERY = 'skip_bigquery'
# Temporary marks
MARK_SKIP_ATHENA_TODO = 'skip_athena_todo'
MARK_SKIP_BIGQUERY_TODO = 'skip_bigquery_todo'


class DB(Enum):
    POSTGRES = 'postgres'
    BIGQUERY = 'bigquery'
    ATHENA = 'athena'


_ENGINE_CACHE: Dict[DB, Engine] = {}
_RECORDED_TEST_TABLES_PER_ENGINE: [Engine, List[str]] = defaultdict(list)


@pytest.fixture()
def unique_table_test_name(
    request: SubRequest,
    testrun_uid: str,
) -> str:
    """
    Generates a unique name for tables used for test in order to avoid conflicts when running parallelized test.
    Format for table name is:
        <TEST_NAME>_<TEST_UUID>
    Where:
     - TEST_NAME is the name of the test being executed (max length = 30 characters)
     - TEST_UUID is the unique id assigned to the call.

    Each generated table name is recorded for the pytest session.
    """
    if 'engine' in request.fixturenames:
        engine = request.node.funcargs['engine']
    else:
        raise Exception('can only generate table name if test uses engine fixtures.')

    # sqlalchemy will raise an error if we exceed this length
    _MAX_LENGTH_TABLE_NAME = 63

    # testrun_uid is an UUID
    _TEST_RUN_ID_LENGTH = 32

    current_test_name = request.node.originalname[:_MAX_LENGTH_TABLE_NAME - _TEST_RUN_ID_LENGTH - 1]
    table_name = f'{current_test_name}_{testrun_uid}'

    _RECORDED_TEST_TABLES_PER_ENGINE[engine].append(table_name)
    return table_name


def pytest_addoption(parser: Parser):
    # Add options for parameterizing multi-database tests for testing either Postgres, Bigquery, or both.
    # The actual parameterizing happens in pytest_generate_tests(), based on the paramters that the user
    # provides

    # This function will automatically be called by pytest at the start of a test run, see:
    # https://docs.pytest.org/en/6.2.x/reference.html#initialization-hooks
    parser.addoption('--postgres', action='store_true', help='run the tests for Postgres')
    parser.addoption('--big-query', action='store_true', help='run the tests for BigQuery')
    parser.addoption('--athena', action='store_true', help='run the tests for Athena')
    parser.addoption('--all', action='store_true', help='run the tests for all databases.')


def pytest_sessionstart(session: Session):
    # Initialize _ENGINE_CACHE per pytest-xdist worker session based on current pytest running config.
    # This way we avoid the creation of a new engine per test, as this is quite inefficient and might
    # cause failures due to multiple clients trying to connect to db server.

    # For more information, please see:
    # https://pytest-xdist.readthedocs.io/en/latest/distribution.html
    # https://docs.pytest.org/en/6.2.x/reference.html#pytest.hookspec.pytest_sessionstart

    if session.config.getoption("all"):
        _ENGINE_CACHE[DB.POSTGRES] = _get_postgres_engine()
        _ENGINE_CACHE[DB.BIGQUERY] = _get_bigquery_engine()
        _ENGINE_CACHE[DB.ATHENA] = _get_athena_engine()
    else:
        if session.config.getoption("athena"):
            _ENGINE_CACHE[DB.ATHENA] = _get_athena_engine()
        if session.config.getoption("big_query"):
            _ENGINE_CACHE[DB.BIGQUERY] = _get_bigquery_engine()
        if session.config.getoption("postgres"):
            _ENGINE_CACHE[DB.POSTGRES] = _get_postgres_engine()
    if not _ENGINE_CACHE:
        # default option: always run tests on postgres
        _ENGINE_CACHE[DB.POSTGRES] = _get_postgres_engine()


def pytest_sessionfinish() -> None:
    # Drops all unique table names generated by unique_table_test_name fixture after all tests
    # ran by current session
    # This way we clean the testing database
    for engine, tables_to_drop in _RECORDED_TEST_TABLES_PER_ENGINE.items():
        with engine.connect() as conn:
            drop_tables_sql = '\n'.join(
                f'DROP TABLE IF EXISTS {table_name};'
                for table_name in tables_to_drop
            )
            conn.execute(drop_tables_sql)


def pytest_generate_tests(metafunc: Metafunc):
    # Paramaterize the 'engine' and 'dialect' parameters of tests based on the options specified by the
    # user (see pytest_addoption() for options).

    # This function will automatically be called by pytest while it is creating the list of tests to run,
    # see: https://docs.pytest.org/en/6.2.x/reference.html#collection-hooks
    markers = list(metafunc.definition.iter_markers())
    skip_postgres = any(mark.name == MARK_SKIP_POSTGRES for mark in markers)
    skip_athena = any(mark.name == MARK_SKIP_ATHENA for mark in markers)
    skip_bigquery = any(mark.name == MARK_SKIP_BIGQUERY for mark in markers)

    skip_athena_todo = any(mark.name == MARK_SKIP_ATHENA_TODO for mark in markers)
    skip_bigquery_todo = any(mark.name == MARK_SKIP_BIGQUERY_TODO for mark in markers)

    engines = []
    for name, engine_dialect in _ENGINE_CACHE.items():
        if name == DB.POSTGRES and skip_postgres:
            continue
        if name == DB.BIGQUERY and (skip_bigquery or skip_bigquery_todo):
            continue
        if name == DB.ATHENA and (skip_athena or skip_athena_todo):
            continue
        engines.append(engine_dialect)

    if 'dialect' in metafunc.fixturenames:
        dialects = [engine.dialect for engine in engines]
        metafunc.parametrize("dialect", dialects)
    if 'engine' in metafunc.fixturenames:
        metafunc.parametrize("engine", engines)


def pytest_collection_modifyitems(session, config, items: List[pytest.Item]):
    # Unit tests should be quick. Add a timeout, after which the test will be cancelled and failed. This is
    # enforced by pytest-timeout. We actually have a few unittests that previously would have taken minutes
    # to run. Having this timeout should prevent performance regressions.

    # This function will automatically be callled by pytest when it has collected all tests to run,
    # see https://docs.pytest.org/en/6.2.x/reference.html#pytest.hookspec.pytest_collection_modifyitems
    for item in items:
        # Check if item is a unittest. This is a bit hackish, but should work on virtual all setups.
        if '/unit/' in str(item.fspath):
            # 1.0 seconds is actual lenient. Almost all tests run within 0.1 on a fast laptop, and even the
            # slowest tests consistently run within 0.5 on a fast laptop.
            item.add_marker(pytest.mark.timeout(1.0))


def pytest_runtest_setup(item: Function):
    # Here we check that tests that are marked as `db_independent`, that they do not have a `dialect` or
    # `engine` parameter.

    # This function will automatically be called by pytest before running a specific test function. See:
    # https://docs.pytest.org/en/6.2.x/reference.html#test-running-runtest-hooks
    fixture_names = item.fixturenames
    markers = list(item.iter_markers())
    is_db_independent_test = any(mark.name == MARK_DB_INDEPENDENT for mark in markers)
    is_multi_db_test = 'dialect' in fixture_names or 'engine' in fixture_names
    if is_db_independent_test and is_multi_db_test:
        raise Exception('Test has both the `db_independent` mark as well as either the `dialect` or '
                        '`engine` parameter. Test can not be both database independent and multi-database.')


def _get_postgres_engine() -> Engine:
    return create_engine(_DB_PG_TEST_URL)


def _get_bigquery_engine() -> Engine:
    return create_engine(_DB_BQ_TEST_URL, credentials_path=_DB_BQ_CREDENTIALS_PATH)


def _get_athena_engine() -> Engine:
    if _DB_ATHENA_TEST_URL:
        return create_engine(_DB_ATHENA_TEST_URL)
    aws_access_key_id = quote_plus(_DB_ATHENA_AWS_ACCESS_KEY_ID)
    aws_secret_access_key = quote_plus(_DB_ATHENA_AWS_SECRET_ACCESS_KEY)
    region_name = quote_plus(_DB_ATHENA_REGION_NAME)
    schema_name = quote_plus(_DB_ATHENA_SCHEMA_NAME)
    s3_staging_dir = quote_plus(_DB_ATHENA_S3_STAGING_DIR)
    athena_work_group = quote_plus(_DB_ATHENA_WORK_GROUP)

    url = (
        f'awsathena+rest://'
        f'{aws_access_key_id}:{aws_secret_access_key}'
        f'@athena.{region_name}.amazonaws.com:443/'
        f'{schema_name}?s3_staging_dir={s3_staging_dir}&work_group={athena_work_group}')
    return create_engine(url)
