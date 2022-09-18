"""
Copyright 2021 Objectiv B.V.
"""
import uuid
import flask
from flask import Response
from objectiv_backend.common.config import get_collector_config
from objectiv_backend.common.types import CookieIdSource
from objectiv_backend.schema.schema import CookieIdContext


def get_json_response(status: int, msg: str, anonymous_mode: bool = False, client_session_id: str = None) -> Response:
    """
    Create a Response object, with json content, and a cookie set if needed.
    :param status: http status code
    :param msg: valid json string
    :param anonymous_mode: bool
    :param client_session_id: str
    """
    response = Response(mimetype='application/json', status=status, response=msg)

    # No cookies if in anonymous mode
    if not anonymous_mode:
        cookie_config = get_collector_config().cookie
        if cookie_config:
            if not client_session_id:
                client_session_id = ''
            cookie_id_context = get_cookie_id_context(anonymous_mode=anonymous_mode, client_session_id=client_session_id)
            cookie_id = cookie_id_context.cookie_id

            response.set_cookie(key=cookie_config.name, value=f'{cookie_id}',
                                max_age=cookie_config.duration, samesite=cookie_config.samesite,
                                secure=cookie_config.secure)
    return response


def get_cookie_id_context(anonymous_mode: bool, client_session_id: str) -> CookieIdContext:
    """
    Create CookieIdContext, based on mode and presence of client_session_id
    :param anonymous_mode: bool
    :param client_session_id: str
    :return: CookieIdContext
    """
    if anonymous_mode:
        cookie_id = client_session_id
        cookie_source = CookieIdSource.CLIENT
    else:
        cookie_id = get_cookie_id_from_cookie(generate_if_not_set=(client_session_id is None))
        if not cookie_id:
            cookie_id = client_session_id
            cookie_source = CookieIdSource.CLIENT
        else:
            cookie_source = CookieIdSource.BACKEND

    return CookieIdContext(id=str(cookie_source), cookie_id=cookie_id)


def get_cookie_id_from_cookie(generate_if_not_set: bool = False) -> str:
    """
    Get the tracking cookie uuid from the current request.
    If no tracking cookie is present in the current request, a random uuid is generated.
    The generated random uuid is stored, so multiple invocations of this function within a request will
    return the same value.

    :raise Exception: If cookies are not configured
    """
    cookie_config = get_collector_config().cookie
    if not cookie_config:
        raise Exception('Cookies are not configured')  # This is a bug. We shouldn't call this function.
    cookie_id = flask.request.cookies.get(cookie_config.name, None)

    if not cookie_id:
        # There's no cookie in the request, perhaps we already generated one earlier in this request
        cookie_id = flask.g.get('G_COOKIE_ID')

    if not cookie_id and generate_if_not_set:
        # There's no cookie in the request, and we have not yet generated one
        # use uuid4 (random), so there is no predictability and bad actors cannot ruin sessions of others
        cookie_id = str(uuid.uuid4())
        flask.g.G_COOKIE_ID = cookie_id
        print(f'Generating cookie_id: {cookie_id}')

    if cookie_id:
        return cookie_id
    else:
        return ''
