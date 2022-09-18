import json
import jsonschema
import base64
import re
from copy import deepcopy
from objectiv_backend.snowplow.schema.ttypes import CollectorPayload
from objectiv_backend.snowplow.snowplow_helper import make_snowplow_custom_contexts, \
    objectiv_event_to_snowplow_payload, snowplow_schema_violation_json
from tests.schema.test_schema import CLICK_EVENT_JSON, make_event_from_dict, make_context
from objectiv_backend.common.config import SnowplowConfig
from objectiv_backend.common.types import CookieIdSource
from objectiv_backend.common.event_utils import get_context, add_global_context_to_event
from objectiv_backend.schema.validate_events import EventError, ErrorInfo


config = SnowplowConfig(
    schema_contexts='test-schema-contexts',
    schema_payload_data='test-schema-payload-data',
    schema_objectiv_taxonomy='test-schema-objectiv-taxonomy',
    schema_objectiv_location_stack='test-schema-objectiv-location-stack',
    schema_objectiv_contexts_base='test-schema-objectiv-contexts-base',
    schema_objectiv_contexts_version='test-schema-objectiv-contexts-version',
    schema_collector_payload='',
    schema_schema_violations='https://raw.githubusercontent.com/snowplow/iglu-central/master/schemas/com.snowplowanalytics.snowplow.badrows/schema_violations/jsonschema/2-0-0',

    gcp_enabled=False,
    gcp_project='',
    gcp_pubsub_topic_raw='',
    gcp_pubsub_topic_bad='',

    aws_enabled=False,
    aws_message_topic_raw='',
    aws_message_topic_bad='',
    aws_message_raw_type=''
)

event_list = json.loads(CLICK_EVENT_JSON)
event = make_event_from_dict(event_list['events'][0])


def test_make_snowplow_custom_context():
    encoded_context = make_snowplow_custom_contexts(event=event, config=config)

    json_context = base64.b64decode(encoded_context)
    context = json.loads(json_context)

    # check that this is in fact a context conforming to the contexts schema we set
    assert context['schema'] == config.schema_contexts

    sp_global_context_data = context['data']

    pattern = re.compile(f'^(.*?)/([a-zA-Z]+)?/jsonschema/{config.schema_objectiv_contexts_version}$')
    for gc_data in sp_global_context_data:

        matches = pattern.match(gc_data['schema'])

        if matches and matches[1] == config.schema_objectiv_contexts_base:
            context_type = matches[2]
            # check to see the data is still the same as the original event
            # we remove '_type' as that is not in the snowplow global contexts, as they are typed in the db/column
            assert gc_data['data'] == {k: v for k, v in get_context(event, context_type).items() if k != '_type'}


def test_objectiv_event_to_snowplow_payload():
    local_event = deepcopy(event)

    context_vars = {
        '_type': 'CookieIdContext',
        'id': CookieIdSource.CLIENT,
        'cookie_id': 'abcde-some-fake-uuid'
    }
    context = make_context(**context_vars)

    add_global_context_to_event(local_event, context)

    collector_payload = objectiv_event_to_snowplow_payload(event=local_event, config=config)
    # check if we get the proper object
    assert type(collector_payload) == CollectorPayload

    # check if the schema is correct
    assert collector_payload.schema == config.schema_collector_payload

    body = json.loads(collector_payload.body)
    # check the schema of the body attribute
    assert body['schema'] == config.schema_payload_data

    # check if we can deserialize the encoded custom context properly
    assert json.loads(base64.b64decode(body['data'][0]['cx']))

    # as the id of the CookieIdContext is set to client, 'sid' should be set
    assert body['data'][0]['sid'] == context_vars['cookie_id']


def test_objectiv_event_to_snowplow_mapping():
    collector_payload = objectiv_event_to_snowplow_payload(event=event, config=config)

    body = json.loads(collector_payload.body)
    data = body['data'][0]

    mapping = {
        'id': 'eid',
        '_type': 'se_ac',
        'time': 'ttm',
        'transport_time': 'stm',
        'corrected_time': 'dtm'
    }

    for obj, sp in mapping.items():
        assert str(event[obj]) == data[sp]

    # check _types
    assert event['_types'] == json.loads(data['se_ca'])


def test_snowplow_failed_event():
    # as we do no actual validation of the event, there's no need to use an invalid event.
    event_error = EventError(
        event_id=event['id'],
        error_info=[
            ErrorInfo(
                data=[],
                info='test')
        ])

    payload = objectiv_event_to_snowplow_payload(event=event, config=config)
    violation = snowplow_schema_violation_json(payload=payload, config=config, event_error=event_error)

    # local copy of https://raw.githubusercontent.com/snowplow/iglu-central/master/schemas/com.snowplowanalytics.snowplow.badrows/schema_violations/jsonschema/2-0-0
    with open('tests/collector/schema_violations.json') as fp:
        schema = json.load(fp)

        # somehow doesn't like the self-describing schema schema from Snowplow
        # so remove it, so we fall back to a generic schema (which is used to validate the schema, not the event)
        del schema['$schema']
        instance = violation['data']

        jsonschema.validate(instance=instance, schema=schema,)
