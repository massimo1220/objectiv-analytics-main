import re
from enum import Enum
from typing import List


class CellTags(Enum):
    INJECTED_ENGINE_VARIABLES = 'injected-engine-variables'
    PANDAS_OUTPUT = 'pandas-output'
    COMMENTED = 'commented'
    SQL_MARKDOWN = 'sql-markdown'
    GET_OBJECTIV_DATAFRAME = 'get_objectiv_dataframe_call'

    NO_OUTPUT = 'no_output'

    @classmethod
    def get_tags(cls, source: str) -> List['CellTags']:
        _HAS_PANDAS_OUTPUT_REGEX = re.compile(r'.*\.(head|to_pandas)\(.*\).*')
        stmts = [stmt for stmt in source.splitlines() if stmt.strip()]
        tags = []
        if all(stmt.startswith('#') for stmt in stmts):
            return [cls.COMMENTED]

        if _HAS_PANDAS_OUTPUT_REGEX.match(stmts[-1]):
            tags.append(cls.PANDAS_OUTPUT)

        if 'display_sql_as_markdown' in stmts[-1]:
            tags.append(cls.SQL_MARKDOWN)

        if 'get_objectiv_dataframe' in source:
            tags.append(cls.GET_OBJECTIV_DATAFRAME)

        if tags:
            return tags
        return [cls.NO_OUTPUT]
