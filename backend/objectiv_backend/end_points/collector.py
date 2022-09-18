import json
from datetime import datetime

import flask
import time
from urllib.parse import urlparse, parse_qs
from typing import List, Callable
import hashlib
import psycopg2
from flask import Response, Request

from objectiv_backend.common.config import get_collector_config, AnonymousModeConfig
from objectiv_backend.common.types import EventData, EventDataList, EventList
from objectiv_backend.common.db import get_db_connection
from objectiv_backend.common.event_utils import add_global_context_to_event, get_contexts
from objectiv_backend.end_points.common import get_json_response, get_cookie_id_context
from objectiv_backend.end_points.extra_output import events_to_json, write_data_to_fs_if_configured, \
    write_data_to_s3_if_configured, write_data_to_snowplow_if_configured
from objectiv_backend.schema.validate_events import validate_structure_event_list, EventError
from objectiv_backend.workers.pg_queues import PostgresQueues, ProcessingStage
from objectiv_backend.workers.pg_storage import insert_events_into_nok_data
from objectiv_backend.workers.worker_entry import process_events_entry
from objectiv_backend.workers.worker_finalize import insert_events_into_data

from objectiv_backend.schema.schema import HttpContext, MarketingContext

# Some limits on the inputs we accept
DATA_MAX_SIZE_BYTES = 1_000_000
DATA_MAX_EVENT_COUNT = 1_000


def anonymous() -> Response:
    return collect(anonymous_mode=True)


def collect(anonymous_mode: bool = False) -> Response:
    """
    Endpoint that accepts event data from the tracker and stores it for further processing.
    """
    current_millis = round(time.time() * 1000)
    try:
        event_data: EventList = _get_event_data(flask.request)
        events: EventDataList = event_data['events']
        transport_time: int = event_data['transport_time']
    except ValueError as exc:
        print(f'Data problem: {exc}')  # todo: real error logging
        return _get_collector_response(error_count=1, event_count=-1, data_error=exc.__str__(),
                                       anonymous_mode=anonymous_mode)

    # check for SessionContext to get client session id
    if 'client_session_id' in event_data:
        # TEMPORARY: we remove the first 7 characters from the string ('client-'), because we only want the uuid
        # part of the client_session_id. This can go when the tracker provides a proper uuid
        # TODO: remove the string slicing
        if event_data['client_session_id'].startswith('client-'):
            client_session_id = event_data['client_session_id'][7:]
        else:
            client_session_id = event_data['client_session_id']
    else:
        client_session_id = None

    # Do all the enrichment steps that can only be done in this phase
    add_enriched_contexts(events, anonymous_mode=anonymous_mode, client_session_id=client_session_id)

    set_time_in_events(events, current_millis, transport_time)

    config = get_collector_config()
    if anonymous_mode:
        # in anonymous mode we hash certain properties, as defined in config.anonymous_mode.to_hash
        anonymize_events(events, config.anonymous_mode)

    if not get_collector_config().async_mode:
        ok_events, nok_events, event_errors = process_events_entry(events=events, current_millis=current_millis)
        print(f'ok_events: {len(ok_events)}, nok_events: {len(nok_events)}')
        write_sync_events(ok_events=ok_events, nok_events=nok_events, event_errors=event_errors)
        return _get_collector_response(error_count=len(nok_events), event_count=len(events), event_errors=event_errors,
                                       anonymous_mode=anonymous_mode, client_session_id=client_session_id)
    else:
        write_async_events(events=events)
        return _get_collector_response(error_count=0, event_count=len(events),
                                       client_session_id=client_session_id)


def hash_property(property_to_hash: str) -> str:
    return hashlib.md5(str(property_to_hash).encode()).hexdigest()


def anonymize_events(events: EventDataList, config: AnonymousModeConfig, hash_method: Callable = hash_property):
    """
    Modify events in the list, by hashing the fields as specified in the config
    :param events: List of events to anonymize
    :param config: AnonymousModeConfig,
    :param hash_method: Callable to hash property with
    :return:
    """
    for event in events:
        for context_type in config.to_hash:
            for context in get_contexts(event, context_type):
                for context_property in config.to_hash[context_type]:
                    context[context_property] = hash_method(context[context_property])


def _get_event_data(request: Request) -> EventList:
    """
    Parse the requests data as json and return as a list

    :raise ValueError:
        1) the data structure is bigger than DATA_MAX_SIZE_BYTES
        2) the data could not be parsed as JSON
        3) the parsed data isn't a valid dictionary
        4) the key 'events' could not be found in the dictionary
        5) event_data['events'] is not a list
        6) there are more than DATA_MAX_EVENT_COUNT events in the event list
        7) the structure did not validate as a valid EventList (validate_structure_event_list()

    :param request: Request from which to parse the data
    :return: the parsed data, an EventList (structure as sent by the tracker)
    """
    post_data = request.data
    if len(post_data) > DATA_MAX_SIZE_BYTES:
        # if it's more than a megabyte, we'll refuse to process
        raise ValueError(f'Data size exceeds limit')
    event_data: EventList = json.loads(post_data)
    if not isinstance(event_data, dict):
        raise ValueError('Parsed post data is not a dict')
    if 'events' not in event_data:
        raise ValueError('Could not find events key in event_data')
    if not isinstance(event_data['events'], list):
        raise ValueError('events is not a list')
    if len(event_data['events']) > DATA_MAX_EVENT_COUNT:
        raise ValueError('Events exceeds limit')
    error_info = validate_structure_event_list(event_data=event_data)
    if error_info:
        raise ValueError(f'List of Events not structured well: {error_info[0].info}')

    return event_data


def _get_collector_response(error_count: int,
                            event_count: int,
                            event_errors: List[EventError] = None,
                            data_error: str = '',
                            anonymous_mode: bool = False,
                            client_session_id: str = None) -> Response:
    """
    Create a Response object, with a json message with event counts, and a cookie set if needed.
    """

    if not get_collector_config().error_reporting:
        event_errors = []
        data_error = ''
    else:
        if event_errors is None:
            event_errors = []

    status = 200 if error_count == 0 else 400
    msg = json.dumps({
        "status": f"{status}",
        "error_count": error_count,
        "event_count": event_count,
        "event_errors": event_errors,
        "data_error": data_error
    })
    # we always return a HTTP 200 status code, so we can handle any errors
    # on the application layer.
    return get_json_response(status=200, msg=msg, anonymous_mode=anonymous_mode, client_session_id=client_session_id)


def add_enriched_contexts(events: EventDataList, anonymous_mode: bool, client_session_id: str):
    """
    Enrich the list of events
    """

    add_cookie_id_context(events, anonymous_mode=anonymous_mode, client_session_id=client_session_id)
    for event in events:
        add_http_context_to_event(event=event, request=flask.request)
        add_marketing_context_to_event(event=event)


def add_cookie_id_context(events: EventDataList, anonymous_mode: bool, client_session_id: str) -> None:
    """
    In anonymous mode we only consider the client_session_id. In normal mode, we check for a cookie, but if the
    client_session_id is set, we don't generate a cookie, but rather "promote" the client_session_id
    :param events: List of events
    :param anonymous_mode:
    :param client_session_id:
    :return:
    """
    cookie_id_context = get_cookie_id_context(anonymous_mode=anonymous_mode, client_session_id=client_session_id)

    for event in events:
        add_global_context_to_event(event, cookie_id_context)


def set_time_in_events(events: EventDataList, current_millis: int, client_millis: int):
    """
    Modify the given list of events: Set the correct time in the events

    We use the `http x-transport-time` header to determine an offset (if any) between client and server time. We
    then correct `event.time` using this offset and set it in `event.time`
    :param events: List of events to modify
    :param current_millis: time in milliseconds since epoch UTC, when this request was received.
    :param client_millis: time sent by client.
    """

    if not client_millis:
        client_millis = current_millis

    offset = current_millis - client_millis
    for event in events:
        # here we correct the tracking time with the calculated offset
        # the assumption here is that transport time should be the same as the server time (current_millis)
        # to account for clients that have an out-of-sync clock
        # this means we have the following timestamps in an event:
        # time: timestamp when the event occurred according to the client
        # corrected_time: timestamp when the event occurred, corrected for transport latency
        # transport_time: timestamp when the event was sent by the client-side transport layer
        # collector_time: timestamp when the collector received the event to process it
        event['corrected_time'] = event['time'] + offset
        event['transport_time'] = client_millis
        event['collector_time'] = current_millis


def _get_remote_address(request: Request) -> str:
    """
    try to determine the IP address of the calling user agent, by looking at some standard headers
    if they aren't set, we fall back to 'remote_addr', which is the connecting client. In most
    cases this is probably wrong.
    :param request: original http request
    :return: string with ip address
    """

    x_forwarded_hosts = str(request.headers.get('X-Forwarded-For', '')).split()
    if 'X-Real-IP' in request.headers:
        # any upstream proxy probably know the 'right' IP. If it sets the x-real-ip header to that,
        # we use that.
        return request.headers['X-Real-IP']
    elif x_forwarded_hosts:
        # x-forwarded-for headers take the form of:
        # client proxy_1...proxy_n
        # we're interested in proxy_n, which is the last node that connects to us, and as such
        # has to be an Internet routed proxy. proxies before it, including the client may be internal
        # and non-routable addresses.
        return x_forwarded_hosts[-1]
    elif request.remote_addr:
        # if all else fails, look for remote_addr in the request. This is the IP the current connection
        # originates from. Most likely a proxy (which is why this is the last resort).
        return request.remote_addr

    # this should never happen!
    return 'unknown'


def add_http_context_to_event(event: EventData, request: Request):
    """
        Create or enrich an HttpContext based on the data in the current request. If an HttpContext is already
        present, the remote address is added to the existing context. Otherwise, a new context is created and
        added to the global_contexts[] of the provided event.

        :param event - event to add context to
        :param request - request object, used to extract extra context from.
    """

    remote_address = _get_remote_address(request)

    # check if there is a pre-existing http_context
    # if so, use that.
    contexts = get_contexts(event, 'HttpContext')
    if contexts:
        tracker_http_context = contexts[0]
        tracker_http_context['remote_address'] = remote_address
    else:
        # if a pre-existing context cannot be found, we create one from scratch
        http_context = {
            'id': 'http_context',
            'remote_address': remote_address,
            'referrer': request.headers.get('Referer', ''),
            'user_agent': request.headers.get('User-Agent', '')
        }

        add_global_context_to_event(event, HttpContext(**http_context))


def add_marketing_context_to_event(event: EventData) -> None:
    """
    Tries to generate MarketingContext(s) based on parameters in the query string, and add to global contexts
    in the provided event.
    :param event: EventData
    :return:
    """
    path_contexts = get_contexts(event, 'PathContext')

    if not path_contexts:
        # without a PathContext, we have no query_string
        return
    else:
        path_context = path_contexts[0]

    query_string = urlparse(str(path_context.get('id', ''))).query
    parsed_qs = parse_qs(query_string)

    # for now, we only support utm, but other mappings are possible
    # all mappings that result in a valid MarketingContext will be added
    mappings = {
        'utm': {
            'source': 'utm_source',
            'medium': 'utm_medium',
            'campaign': 'utm_campaign',
            'term': 'utm_term',
            'content': 'utm_content',
            'source_platform': 'utm_source_platform',
            'creative_format': 'utm_creative_format',
            'marketing_tactic': 'utm_marketing_tactic',
        }
    }

    for mapping_type in mappings:
        mapping = mappings[mapping_type]
        marketing_context_fields = {}
        for field, mapped_field in mapping.items():

            # only add the field, if it is present in the query string
            # we don't set default values for missing fields here. If the fields are optional
            # the MarketingContext class will handle this, or simply fail, which is also OK.
            if mapped_field in parsed_qs:
                value = parsed_qs[mapped_field][0]
                marketing_context_fields[field] = str(value)

        marketing_context_fields['id'] = mapping_type

        if len(marketing_context_fields) > 1:
            # if no fields are set (other than id), no point in trying
            try:
                add_global_context_to_event(event, MarketingContext(**marketing_context_fields))
            except TypeError as e:
                # couldn't create a marketing context for this mapping, no problem, as this is not a mandatory context
                #
                # This way, the MarketingContext class decides whether sufficient / appropriate arguments are supplied
                # to create a valid instance (that adheres to the schema), no need to implement that logic here.
                pass


def write_sync_events(ok_events: EventDataList, nok_events: EventDataList, event_errors: List[EventError] = None):
    """
    Write the events to the following sinks, if configured:
        * postgres
        * aws
        * file system
    """
    output_config = get_collector_config().output
    # todo: add exception handling. if one output fails, continue to next if configured.
    if output_config.postgres:
        try:
            connection = get_db_connection(output_config.postgres)
            try:
                with connection:
                    insert_events_into_data(connection, events=ok_events)
                    insert_events_into_nok_data(connection, events=nok_events)
            finally:
                connection.close()
        except psycopg2.DatabaseError as oe:
            print(f'Error occurred in postgres: {oe}')

    if output_config.snowplow:
        write_data_to_snowplow_if_configured(events=ok_events, good=True)
        write_data_to_snowplow_if_configured(events=nok_events, good=False, event_errors=event_errors)

    if not output_config.file_system and not output_config.aws:
        return
    for prefix, events in ('OK', ok_events), ('NOK', nok_events):
        if events:
            data = events_to_json(events)
            moment = datetime.utcnow()
            write_data_to_fs_if_configured(data=data, prefix=prefix, moment=moment)
            write_data_to_s3_if_configured(data=data, prefix=prefix, moment=moment)


def write_async_events(events: EventDataList):
    """
    Write the events to the following sinks, if configured:
        * postgres - To the entry queue
        * aws - to the 'RAW' prefix
        * file system - to the 'RAW' directory
    """
    output_config = get_collector_config().output
    # todo: add exception handling. if one output fails, continue to next if configured.
    if output_config.postgres:
        connection = get_db_connection(output_config.postgres)
        try:
            with connection:
                pg_queue = PostgresQueues(connection=connection)
                pg_queue.put_events(queue=ProcessingStage.ENTRY, events=events)
        finally:
            connection.close()

    if not output_config.file_system and not output_config.aws:
        return
    prefix = 'RAW'
    if events:
        data = events_to_json(events)
        moment = datetime.utcnow()
        write_data_to_fs_if_configured(data=data, prefix=prefix, moment=moment)
        write_data_to_s3_if_configured(data=data, prefix=prefix, moment=moment)

