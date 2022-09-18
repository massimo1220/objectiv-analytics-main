"""
Copyright 2022 Objectiv B.V.
"""
import re
import string
import warnings


CODES_SUPPORTED_IN_ALL_DIALECTS = {
    # These are the codes that we support for all database dialects.

    # week codes
    '%a',  # WEEKDAY_ABBREVIATED
    '%A',  # WEEKDAY_FULL_NAME

    # day codes
    '%d',  # DAY_OF_MONTH
    '%j',  # DAY_OF_YEAR

    # month codes
    '%b',  # MONTH_ABBREVIATED
    '%B',  # MONTH_FULL_NAME
    '%m',  # MONTH_NUMBER

    # year codes
    '%y',  # YEAR_WITHOUT_CENTURY
    '%Y',  # YEAR_WITH_CENTURY

    # time unit codes
    '%H',  # HOUR24
    '%I',  # HOUR12
    '%M',  # MINUTE
    '%S',  # SECOND

    # format codes
    '%F',  # YEAR_MONTH_DAY
    '%R',  # HOUR_MINUTE
    '%T',  # HOUR_MINUTE_SECOND

    # special characters
    '%%',  # PERCENT_CHAR
}

STRINGS_SUPPORTED_IN_ALL_DIALECTS = [
    # These are the combinations of codes that we support for all database dialects, even if some of the
    # individual codes are not supported.
    # When adding more strings here: Strings must be sorted longest to shortest, and all strings must
    # start with a percentage sign.

    '%S.%f',  # <seconds>.<microsecnds>
]


_SUPPORTED_C_STANDARD_CODES = {
    # week codes
    '%a',  # WEEKDAY_ABBREVIATED
    '%A',  # WEEKDAY_FULL_NAME
    '%w',  # WEEKDAY_NUMBER
    '%U',  # WEEK_NUMBER_OF_YEAR_SUNDAY_FIRST
    '%W',  # WEEK_NUMBER_OF_YEAR_MONDAY_FIRST

    # day codes
    '%d',  # DAY_OF_MONTH
    '%e',  # DAY_OF_MONTH_PRECEDED_BY_A_SPACE
    '%j',  # DAY_OF_YEAR

    # month codes
    '%b',  # MONTH_ABBREVIATED
    '%h',  # MONTH_ABBREVIATED_2
    '%B',  # MONTH_FULL_NAME
    '%m',  # MONTH_NUMBER

    # year codes
    '%y',  # YEAR_WITHOUT_CENTURY
    '%Y',  # YEAR_WITH_CENTURY
    '%C',  # CENTURY
    '%Q',  # QUARTER
    '%D',  # MONTH_DAY_YEAR

    # iso 8601 codes
    '%G',  # ISO_8601_YEAR_WITH_CENTURY
    '%g',  # ISO_8601_YEAR_WITHOUT_CENTURY
    '%V',  # ISO_8601_WEEK_NUMBER_OF_YEAR
    '%u',  # ISO_8601_WEEKDAY_NUMBER

    # time unit codes
    '%H',  # HOUR24
    '%I',  # HOUR12
    '%k',  # HOUR24_PRECEDED_BY_A_SPACE
    '%l',  # HOUR12_PRECEDED_BY_A_SPACE
    '%M',  # MINUTE
    '%S',  # SECOND
    '%s',  # EPOCH
    '%f',  # MICROSECOND

    '%z',  # UTC_OFFSET
    '%Z',  # TIME_ZONE_NAME

    # format codes
    '%F',  # YEAR_MONTH_DAY
    '%R',  # HOUR_MINUTE
    '%T',  # HOUR_MINUTE_SECOND

    # special characters
    '%n',  # NEW_LINE
    '%t',  # TAB
    '%%',  # PERCENT_CHAR
}

# https://www.postgresql.org/docs/current/functions-formatting.html#FUNCTIONS-FORMATTING-DATETIME-TABLE
_C_STANDARD_CODES_X_POSTGRES_DATE_CODES = {
    "%a": "Dy",
    "%A": "FMDay",
    "%w": "D",  # Sunday is 1 and Saturday is 7
    "%d": "DD",
    "%j": "DDD",
    "%b": "Mon",
    "%h": "Mon",
    "%B": "FMMonth",
    "%m": "MM",
    "%y": "YY",
    "%Y": "YYYY",
    "%C": "CC",
    "%Q": "Q",
    "%D": "MM/DD/YY",
    "%F": "YYYY-MM-DD",
    "%G": "IYYY",
    "%g": "IY",
    "%V": "IW",
    "%u": "ID",
    "%H": "HH24",
    "%I": "HH12",
    "%M": "MI",
    "%S": "SS",
    "%f": "US",
    "%z": "OF",
    "%Z": "TZ",
    "%R": "HH24:MI",
    "%T": "HH24:MI:SS",
    "%%": "%",
}


def parse_c_standard_code_to_postgres_code(date_format: str) -> str:
    """
    Parses a date format string from standard codes to Postgres date codes.
    If c-standard code has no equivalent, it will remain in resultant string.

    Steps to follow:
        date_format = '%Y%m-%Y%m-%Y%m%d-%d'

        Step 1: Get all unique groups of continuous c-codes,
            groups are processed based on length in order to avoid
            replacing occurrences of other groups (e.g %Y%m occurs in %Y%m%d, but both are different groups):
                ['%Y%m%d', '%Y%m', '%d']

        Step 2: Split initial dateformat by c-code groups

        Step 3: For token from previous step:
            If token is not a supported c-code, then treat the token as a literal and quote it.
                (e.g Year: -> "Year:")
            else:
                1) Get individual codes from token
                2) Replace each code with respective Postgres Code
                3) Recreate group by joining all results from previous step with an empty literal.
                    (e.g %Y%m%d -> YYYY""MM""DD

    .. note:: We use double quotes to force TO_CHAR interpret an empty string as literals, this way
            continuous date codes yield the correct value as intended
            For example having '%y%Y':
              TO_CHAR(cast('2022-01-01' as date), 'YY""YYYY') will generate '222022' (correct)
              vs.
              TO_CHAR(cast('2022-01-01' as date), 'YYYYYY') will generate '202222' (incorrect)

    """

    codes_base_pattern = '|'.join(_SUPPORTED_C_STANDARD_CODES)
    grouped_codes_matches = re.findall(pattern=rf"(?P<codes>(?:{codes_base_pattern})+)", string=date_format)
    if not grouped_codes_matches:
        # return it as a literal
        date_format = date_format.replace('"', r'\"')
        return f'"{date_format}"'

    tokenized_c_codes = sorted(set(grouped_codes_matches), key=len, reverse=True)
    single_c_code_regex = re.compile(rf'{codes_base_pattern}')

    new_date_format_tokens = []
    all_tokens = re.split(pattern=rf"({'|'.join(tokenized_c_codes)})", string=date_format)
    for token in all_tokens:
        # empty space
        if not token:
            continue

        # is a literal
        if token not in tokenized_c_codes:
            formatted_literal = token.replace('"', r'\"')
            new_date_format_tokens.append(f'"{formatted_literal}"')
            continue

        # get individual codes from the group
        codes_to_replace = single_c_code_regex.findall(token)
        replaced_codes = []
        for to_repl_code in codes_to_replace:
            # get correspondent postgres code if it exists, otherwise include to_repl_code unchanged.
            replaced_codes.append(_C_STANDARD_CODES_X_POSTGRES_DATE_CODES.get(to_repl_code, to_repl_code))

        new_date_format_tokens.append('""'.join(replaced_codes))

    return ''.join(new_date_format_tokens)


def parse_c_code_to_athena_code(date_format: str) -> str:
    """
    Parses a date format string, and return a string that's compatible with Athena's date_format() function.

    Some python format codes are different on Athena, or might even raise an error. Such codes are converted
    or escaped; using the returned string with Athena's date_format will never raise an error.

    Codes in CODES_SUPPORTED_IN_ALL_DIALECTS are guaranteed to be correctly represented in the returned
    format string. If date_format contains codes that are not in that set, then the returned format might
    evaluate to a different string than the original date_format would with python's strftime() function.
    """
    # Athena code spec: https://prestodb.io/docs/0.217/functions/datetime.html
    # Python code spec: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
    c_code_to_athena_mapping = {
        # if there is no code, i.e. a lone '%' that's not followed by an alphabetic character, then that
        # should yield '%'. So we want to generate '%%'
        '%': '%%',
        # List supported codes that are not in CODES_SUPPORTED_IN_ALL_DIALECTS
        '%f': '%f',
        # Actual mappings
        '%A': '%W',
        '%M': '%i',
        '%B': '%M',
        '%F': '%Y-%m-%d',
        '%R': '%H:%i',
    }
    codes_to_consider = set(string.ascii_letters + '%')
    result = []
    i = 0
    while i < len(date_format):
        current = date_format[i]
        i += 1
        if current != '%':
            # This is not the start of a code sequence, just a regular character.
            result.append(current)
        else:
            # This is the start of a code sequence.
            if i < len(date_format) and date_format[i] in codes_to_consider:
                current = current + date_format[i]
                i += 1
            if current not in CODES_SUPPORTED_IN_ALL_DIALECTS and current not in c_code_to_athena_mapping:
                # If Athena encounters a code it does not support, then it will do either of:
                # 1) raise an error for a number of specifically not supported codes (%D, %U, %u, %V, %w, %X)
                # 2) only include the second character in the result, but strip the '%' off.
                # The general behaviour of strftime() in python is to just include the ignored code,
                # including the leading '%'. We want to mimic that by always escaping unknown codes.
                result.append(f'%{current}')
            else:
                # map c-codes to athena specific codes
                current = c_code_to_athena_mapping.get(current, current)
                result.append(current)
    return ''.join(result)


def parse_c_code_to_bigquery_code(date_format: str) -> str:
    """
    Replaces all '%S.%f' with '%E6S', since BigQuery does not support microseconds c-code.
    """
    if '%S.%f' in date_format:
        date_format = re.sub(r'%S\.%f', '%E6S', date_format)
    return date_format


def warn_non_supported_format_codes(date_format: str):
    """
    Checks that all formatting codes in date_format are listed in CODES_SUPPORTED_IN_ALL_DIALECTS or are
    part of a string that's listed in STRINGS_SUPPORTED_IN_ALL_DIALECTS.

    If one or more non-listed codes are found, a UserWarning is emitted.
    """
    unsupported_c_codes = set()
    i = 0
    while i < len(date_format):
        current = date_format[i]
        i += 1
        if current != '%':  # This is not the start of a code sequence, just a regular character.
            continue

        # This is the start of a code sequence.
        # See if any of the STRINGS_SUPPORTED_IN_ALL_DIALECTS start at this character
        for supported_string in STRINGS_SUPPORTED_IN_ALL_DIALECTS:
            # Get a string from date_format with the same length as supported_string starting at the current
            # position.
            sub_str_start = i - 1
            sub_str_end = sub_str_start + len(supported_string)
            sub_str = date_format[sub_str_start:sub_str_end]
            if sub_str == supported_string:
                # Match: we know this string is good, and can skip to the end of it.
                i = sub_str_end
                break  # skip the 'else:' clause of this for loop
        else:
            # If we get here, that means that none of the strings in STRINGS_SUPPORTED_IN_ALL_DIALECTS
            # start at the current character.
            # See if the code that starts here is listed in CODES_SUPPORTED_IN_ALL_DIALECTS
            if i < len(date_format):
                current = current + date_format[i]
                i += 1
            if current not in CODES_SUPPORTED_IN_ALL_DIALECTS:
                unsupported_c_codes.add(current)
    if unsupported_c_codes:
        message = f'These formatting codes are not generally supported: ' \
                  f'{", ".join(sorted(unsupported_c_codes))}.' \
                  f'They might not work reliably on some or all database platforms..'
        warnings.warn(
            message=message,
            category=UserWarning,
        )
