"""
Copyright 2021 Objectiv B.V.
"""
from typing import NamedTuple, Optional, List

import sqlparse
from sqlparse.sql import TokenList, Token


class CteTuple(NamedTuple):
    name: Optional[str]
    select_sql: str


def raw_sql_to_selects(sql: str) -> List[CteTuple]:
    """
    Given a raw sql select statement, return a list with all CTEs and the final select statement.

    If the sql consists of a simple query without CTEs then the returned list contains a single item.
    If the sql consists of a CTEs followed by a final select, then the returned list contains all CTEs in
    the encountered order, followed by the select statement.
    For each CTE in the returned value the `name` field is guaranteed to be set, for the final select
    statement it will be None.
    """
    # TODO: refactor function
    stmts = sqlparse.parse(sql)
    if len(stmts) == 0:
        return []

    # if len(stmts) > 1
    #     raise ValueError(f'Expected sql with a single statement, found {len(stmts)} statements.')
    # todo: check that there is one real statement. make sure this check works even if the statement
    #  ends with a semicolon

    stmt = stmts[0]
    tokens = list(stmt.flatten())
    token_list = TokenList(tokens)

    idx_with, _ = token_list.token_next_by(m=(sqlparse.tokens.Keyword.CTE, 'WITH'))
    idx_select, _ = token_list.token_next_by(m=(sqlparse.tokens.DML, 'SELECT'))

    if idx_select is None:
        raise ValueError(f'Cannot find select statement. sql: {sql}')
    if idx_with is None or idx_select < idx_with:
        # This query is a simple select statement
        return [CteTuple(name=None, select_sql=str(stmt))]
    else:
        # This query contains Common Table Expressions
        idx = idx_with
        result = []
        while idx < len(token_list.tokens):
            idx_name, token_name = token_list.token_next_by(idx=idx, t=sqlparse.tokens.Name)
            idx_select, _ = token_list.token_next_by(idx=idx, m=(sqlparse.tokens.DML, 'SELECT'))
            if idx_name is None and idx_select is None:
                raise ValueError(f'Cannot find next CTE or select statement. sql: {sql}')
            if idx_name is None or idx_select < idx_name:
                token_sublist = token_list.tokens[idx_select:]
                result.append(CteTuple(name=None, select_sql=_tokens_to_sql(token_sublist)))
                return result

            # todo: support syntax 'cte_name (column_names) as ...` now we only support 'cte_name as ...'
            idx_as, _ = token_list.token_next_by(idx=idx_name, m=(sqlparse.tokens.Keyword, 'AS'))
            idx_paren_open, _ = token_list.token_next_by(idx=idx_as, m=(sqlparse.tokens.Punctuation, '('))
            idx = idx_paren_open + 1
            paren_open = 1
            while idx < len(token_list.tokens):
                if token_list[idx].match(sqlparse.tokens.Punctuation, '('):
                    paren_open += 1
                elif token_list[idx].match(sqlparse.tokens.Punctuation, ')'):
                    paren_open -= 1
                idx += 1
                if paren_open == 0:
                    # Found the end of the CTE
                    token_sublist = token_list.tokens[(idx_paren_open + 1):(idx - 1)]
                    result.append(
                        CteTuple(name=token_name.normalized, select_sql=_tokens_to_sql(token_sublist))
                    )
                    break
    raise ValueError(f'Reached end of sql code without finding a select statement. sql: {sql}')


def _tokens_to_sql(tokens: List[Token]) -> str:
    return str(TokenList(tokens))
