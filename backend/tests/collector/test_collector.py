import json

import pytest
import flask
from objectiv_backend.app import create_app

from objectiv_backend.end_points.collector import add_http_context_to_event, add_marketing_context_to_event, \
    get_cookie_id_context, anonymize_events, hash_property
from objectiv_backend.end_points.common import get_json_response
from objectiv_backend.common.event_utils import add_global_context_to_event, get_contexts
from objectiv_backend.common.config import AnonymousModeConfig
from objectiv_backend.common.types import CookieIdSource
from tests.schema.test_schema import CLICK_EVENT_JSON, make_event_from_dict, order_dict, make_context


class Request(object):
    headers = {
        'Referer': 'test-referer',
        'User-Agent': 'test-user-agent',
        'X-Real-IP': '256.256.256.256'
    }


HTTP_REQUEST = Request()


def _get_http_context():
    headers = HTTP_REQUEST.headers
    return {
        '_type': 'HttpContext',
        'id': 'http_context',
        'remote_address': headers['X-Real-IP'],
        'referrer': headers['Referer'],
        'user_agent': headers['User-Agent']
    }


def test_add_create_http_context():
    """
    Test that an http context is succesfully added by the collector, if none is present
    """
    event_list = json.loads(CLICK_EVENT_JSON)
    event = make_event_from_dict(event_list['events'][0])
    add_http_context_to_event(event=event, request=HTTP_REQUEST)

    generated_http_contexts = get_contexts(event=event, context_type='HttpContext')

    # will be false if there is none
    assert generated_http_contexts

    # there should be exactly 1 HttpContext
    assert len(generated_http_contexts) == 1

    generated_http_context = generated_http_contexts[0]

    assert(order_dict(generated_http_context) == order_dict(_get_http_context()))


def test_enrich_http_context():
    """
    Test that an http context is successfully enriched by the collector, if one is already present
    """

    event_list = json.loads(CLICK_EVENT_JSON)
    event = make_event_from_dict(event_list['events'][0])

    headers = HTTP_REQUEST.headers
    http_context = {
        '_type': 'HttpContext',
        'id': 'http_context',
        'remote_address': '127.0.0.1',
        'referrer': headers['Referer'],
        'user_agent': headers['User-Agent']
    }
    # add context to event
    add_global_context_to_event(event=event, context=http_context)

    # this should enrich the pre-existing HttpContext
    add_http_context_to_event(event=event, request=HTTP_REQUEST)

    # retrieve http context(s) from event
    generated_http_contexts = get_contexts(event=event, context_type='HttpContext')

    # will be false if there is none
    assert generated_http_contexts

    # there should be exactly 1 HttpContext
    assert len(generated_http_contexts) == 1

    generated_http_context = generated_http_contexts[0]

    assert(order_dict(generated_http_context) == order_dict(_get_http_context()))


def test_enrich_marketing_context():
    event_list = json.loads(CLICK_EVENT_JSON)
    event = make_event_from_dict(event_list['events'][0])

    add_marketing_context_to_event(event=event)

    # there are no utm parameters
    generated_marketing_contexts = get_contexts(event=event, context_type='MarketingContext')
    assert len(generated_marketing_contexts) == 0

    # update path context, with utm params in query string
    path_contexts = get_contexts(event=event, context_type='PathContext')
    path_context = path_contexts[0]

    path_context['id'] = 'http://localhost:3000?' \
                         'utm_source=test-source&' \
                         'utm_medium=test-medium&' \
                         'utm_campaign=test-campaign&' \
                         'utm_term=test-term&' \
                         'utm_source_platform=test-source-platform&' \
                         'utm_creative_format=test-creative-format&' \
                         'utm_marketing_tactic=test-marketing-tactic'

    # call enrichment
    add_marketing_context_to_event(event=event)

    # there should now be exactly one marketing context
    generated_marketing_contexts = get_contexts(event=event, context_type='MarketingContext')
    assert len(generated_marketing_contexts) == 1

    generated_marketing_context = generated_marketing_contexts[0]

    # check optional is properly set
    assert generated_marketing_context['term'] == 'test-term'

    # check that missing optional is not there
    assert not generated_marketing_context['content']

    # dictionary representation of context
    marketing_context = {
        '_type': 'MarketingContext',
        'campaign': 'test-campaign',
        'content': None,
        'creative_format': 'test-creative-format',
        'id': 'utm',
        'marketing_tactic': 'test-marketing-tactic',
        'medium': 'test-medium',
        'source': 'test-source',
        'source_platform': 'test-source-platform',
        'term': 'test-term',
    }

    # (ordered) json representation of dict
    marketing_context_json = '{' \
                             '"_type": "MarketingContext", ' \
                             '"campaign": "test-campaign", ' \
                             '"content": null, ' \
                             '"creative_format": "test-creative-format", ' \
                             '"id": "utm", ' \
                             '"marketing_tactic": "test-marketing-tactic", ' \
                             '"medium": "test-medium", ' \
                             '"source": "test-source", ' \
                             '"source_platform": "test-source-platform", ' \
                             '"term": "test-term"' \
                             '}'
    assert(json.dumps(order_dict(marketing_context))) == marketing_context_json

    # check serialized jsons match for set and unset optionals
    assert json.dumps(order_dict(generated_marketing_context)) == marketing_context_json


@pytest.fixture
def app_context():
    """create the app and return the request context as a fixture
       so that this process does not need to be repeated in each test
    """
    app = create_app()
    return app.test_request_context


def test_cookie_id_context_creation(mocker, app_context):
    with app_context():
        event_list = json.loads(CLICK_EVENT_JSON)
        client_session_id = event_list['client_session_id']

        # in anonymous mode, the id should always be client
        context = get_cookie_id_context(anonymous_mode=True, client_session_id=client_session_id)
        assert context.id == CookieIdSource.CLIENT
        assert context.cookie_id == client_session_id

        # Pure Anonymous mode
        # mock the flask request property, this is used to retrieve cookies
        request_mock = mocker.patch.object(flask, 'request')

        # Promotion of anonymous to normal
        # in normal mode, the id should be client if there's no cookie, and a valid client_session_id
        # we use the mock to never return a cookie (but None)
        request_mock.cookies.get = lambda param, default: None
        context = get_cookie_id_context(anonymous_mode=False, client_session_id=client_session_id)
        assert context.id == CookieIdSource.CLIENT
        assert context.cookie_id == client_session_id

        # Pure normal mode
        # normal mode with a cookie set, the mock returns a value for the requested cookie, so
        # the id should be 'backend'
        cookie_id = 'd227e473-b177-4cdc-9f49-a96e59dc00k13'
        request_mock.cookies.get = lambda param, default: cookie_id
        context = get_cookie_id_context(anonymous_mode=False, client_session_id=client_session_id)
        assert context.id == CookieIdSource.BACKEND
        assert context.cookie_id == cookie_id


def test_cookie_set(mocker, app_context):
    with app_context():
        # Pure Anonymous mode
        # mock the flask request property, this is used to retrieve cookies
        request_mock = mocker.patch.object(flask, 'request')
        request_mock.cookies.get = lambda param, default: None
        event_list = json.loads(CLICK_EVENT_JSON)
        msg = 'test'

        client_session_id = event_list['client_session_id']
        status = 200

        # in anonymous mode we should never set cookies
        response = get_json_response(status=status, msg=msg, anonymous_mode=True, client_session_id=client_session_id)
        assert not response.headers.get('Set-Cookie', None)

        # in normal mode, with no cookie set, it should set the cookie to the client_session_id
        response = get_json_response(status=status, msg=msg, anonymous_mode=False, client_session_id=client_session_id)
        cookie = response.headers.get('Set-Cookie', None)
        assert cookie
        # manually get cookie value. this looks something like:
        # obj_user_id=d227e473-b177-4cdc-9f49-a96e59dbcf0c; Expires=Thu, 14 Sep 2023 13:55:24 GMT; Max-Age=31536000; Secure; Path=/; SameSite=None
        assert cookie.split(';')[0].split('=')[1] == client_session_id

        # in normal mode, with no cookie set, it should set the cookie to the client_session_id
        cookie_id = 'd227e473-b177-4cdc-9f49-a96e59dc00k13'
        request_mock.cookies.get = lambda param, default: cookie_id
        response = get_json_response(status=status, msg=msg, anonymous_mode=False, client_session_id=None)
        cookie = response.headers.get('Set-Cookie', None)
        assert cookie
        assert cookie.split(';')[0].split('=')[1] == cookie_id


def test_anonymous_mode_anonymization():

    config = AnonymousModeConfig(
        to_hash={
            'HttpContext': {
                'remote_address',
                'user_agent'
            }
        }
    )

    context_vars = {
        '_type': 'HttpContext',
        'id': 'test-http-context-id',
        'referrer': 'test-referrer',
        'remote_address': 'test-address',
        'user_agent': 'test-user_agent'
    }
    context = make_context(**context_vars)

    # add created context to event
    event_list = json.loads(CLICK_EVENT_JSON)
    event = make_event_from_dict(event_list['events'][0])
    add_global_context_to_event(event, context)

    events = [event]
    anonymize_events(events=events, config=config)

    # retrieve http context from event
    http_context = get_contexts(event, 'HttpContext')[0]

    # check values are in fact changed
    assert http_context['remote_address'] != context_vars['remote_address']
    assert http_context['user_agent'] != context_vars['user_agent']

    # check if we have indeed properly hashed the vars
    assert http_context['user_agent'] == '49901a043486b776d3e9e0aa2b6bf1c1'
    assert hash_property(context_vars['user_agent']) == '49901a043486b776d3e9e0aa2b6bf1c1'
