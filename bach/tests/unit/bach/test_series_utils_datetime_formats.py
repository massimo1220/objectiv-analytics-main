"""
Copyright 2022 Objectiv B.V.
"""
import pytest

from bach.series.utils.datetime_formats import parse_c_standard_code_to_postgres_code, \
    parse_c_code_to_bigquery_code, parse_c_code_to_athena_code, warn_non_supported_format_codes

pytestmark = [pytest.mark.db_independent]  # mark all tests here as database independent.
# Better would be to have a mark called 'db_specific' or something like that.
# The point is that all tests in this file run are specific to a database dialect, and don't need to be run
# for all database dialects.


def test_parse_c_standard_code_to_postgres_code():
    # single c-code
    assert parse_c_standard_code_to_postgres_code('%Y') == 'YYYY'

    # non supported c-code in bach
    assert parse_c_standard_code_to_postgres_code('%c') == '"%c"'

    # c-code supported in bach, not in postgres
    assert parse_c_standard_code_to_postgres_code('%s') == '%s'

    # percentage signs
    assert parse_c_standard_code_to_postgres_code('%Y-%%%m-%d') == 'YYYY"-"%""MM"-"DD'
    assert parse_c_standard_code_to_postgres_code('%%') == '%'
    assert parse_c_standard_code_to_postgres_code('%%Y') == '%"Y"'
    assert parse_c_standard_code_to_postgres_code('%%%Y%%%%') == '%""YYYY""%""%'

    # simple case
    assert parse_c_standard_code_to_postgres_code('%Y-%m-%d') == 'YYYY"-"MM"-"DD'

    # multiple continuous c-codes
    assert parse_c_standard_code_to_postgres_code('%Y%m-%d%d') == 'YYYY""MM"-"DD""DD'

    # date format with extra tokens in start and end
    assert parse_c_standard_code_to_postgres_code('abc %Y def%') == '"abc "YYYY" def%"'

    # continuous c-codes in single string
    assert parse_c_standard_code_to_postgres_code('%Y%Y%Y') == 'YYYY""YYYY""YYYY'

    # nested groups
    assert parse_c_standard_code_to_postgres_code('%Y%m-%Y%m%d-%Y%m-%m%d-%d') == (
        'YYYY""MM"-"YYYY""MM""DD"-"YYYY""MM"-"MM""DD"-"DD'
    )

    # regular postgres format
    assert parse_c_standard_code_to_postgres_code('YYYYMMDD') == '"YYYYMMDD"'


def test_parse_c_code_to_bigquery_code():
    assert parse_c_code_to_bigquery_code('%H:%M:%S.%f') == '%H:%M:%E6S'
    assert parse_c_code_to_bigquery_code('%H:%M:%S.%f %f %S.%f') == '%H:%M:%E6S %f %E6S'


def test_parse_c_code_to_athena_code():
    assert parse_c_code_to_athena_code('%Y-%m-%d') == '%Y-%m-%d'
    assert parse_c_code_to_athena_code('%M-%B') == '%i-%M'
    # Escape not supported codes:
    assert parse_c_code_to_athena_code('%V') == '%%V'
    assert parse_c_code_to_athena_code('%q %1 %_') == '%%q %%1 %%_'
    # Handle double quotes correctly
    assert parse_c_code_to_athena_code('%%%m') == '%%%m'


def test_warn_non_supported_format_codes(recwarn):
    # See https://docs.pytest.org/en/6.2.x/warnings.html#recwarn for docs on pytest.warns()

    # Make sure there are no warning for these, as they are all supported
    warn_non_supported_format_codes('%Y-%m-%d')
    warn_non_supported_format_codes('%H:%M:%S.%f')
    warn_non_supported_format_codes('test %H:%M:%S.%f test')
    warn_non_supported_format_codes('test %H:%M:%S.%f%S.%f%S.%f')
    warn_non_supported_format_codes('%H:%M:%S.%f:%H')
    warn_non_supported_format_codes('%S.%f')
    warn_non_supported_format_codes('%S.%f.%S')
    warn_non_supported_format_codes('%%%%')
    assert len(recwarn) == 0

    # Make sure we get the correct warnings for non-supported codes
    expected_msg_match = "These formatting codes are not generally supported: %f"
    with pytest.warns(UserWarning, match=expected_msg_match):
        warn_non_supported_format_codes('S.%f')
    with pytest.warns(UserWarning, match=expected_msg_match):
        warn_non_supported_format_codes('%f')
    with pytest.warns(UserWarning, match=expected_msg_match):
        warn_non_supported_format_codes('test %f test')
    with pytest.warns(UserWarning, match=expected_msg_match):
        warn_non_supported_format_codes('%S:%f%f')
    with pytest.warns(UserWarning, match=expected_msg_match):
        warn_non_supported_format_codes('%M.%f')
    with pytest.warns(UserWarning, match=expected_msg_match):
        warn_non_supported_format_codes('%S%f')

    expected_msg_match = "These formatting codes are not generally supported: %1, %_, %q"
    with pytest.warns(UserWarning, match=expected_msg_match):
        warn_non_supported_format_codes('%q, %1, %_ %q %H:%M:%S.%f')

    expected_msg_match = "These formatting codes are not generally supported: %n, %t"
    with pytest.warns(UserWarning, match=expected_msg_match):
        warn_non_supported_format_codes('%%%t%n')
