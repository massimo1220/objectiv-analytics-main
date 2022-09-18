from typing import Dict, List, Union, Callable

import base64
import json
from datetime import datetime
from urllib.parse import urlparse

from objectiv_backend.snowplow.schema.ttypes import CollectorPayload  # type: ignore

from objectiv_backend.common.config import SnowplowConfig, get_collector_config
from objectiv_backend.common.event_utils import get_context
from objectiv_backend.common.types import EventDataList, EventData, CookieIdSource
from objectiv_backend.schema.validate_events import EventError

from thrift.protocol import TBinaryProtocol
from thrift.transport import TTransport

# only load imports if needed
output_config = get_collector_config().output

if output_config.snowplow:
    snowplow_config = output_config.snowplow
    if snowplow_config.gcp_enabled:
        from google.cloud import pubsub_v1
        from google.api_core.exceptions import NotFound

        gcp_publisher = pubsub_v1.PublisherClient()

    if snowplow_config.aws_enabled:
        import boto3
        import botocore.exceptions


def filter_dict(data: Dict, filter_keys: List) -> Dict:
    return {k: v for k, v in data.items() if k not in filter_keys}


def make_snowplow_custom_contexts(event: EventData, config: SnowplowConfig) -> str:
    """
    Create Snowplow custom contexts, mapping contexts of an Objectiv Event onto Snowplow custom contexts:
    - global contexts are mapped onto individual custom contexts
    - location stack is mapped as a single object

    returns a list of self describing Snowplow customcontexts, base64 encoded a string

    :param event: List of Dict containing a schema and a payload
    :param config: SnowplowConfig
    :return: base64 encoded snowplow self-describing custom context
    """
    self_describing_contexts = []

    # first add global contexts
    blocked = ['_type', '_types']
    version = config.schema_objectiv_contexts_version
    schema_base = config.schema_objectiv_contexts_base
    for context in event['global_contexts']:
        context_type = context['_type']
        schema = f'{schema_base}/{context_type}/jsonschema/{version}'
        data = filter_dict(context, blocked)
        self_describing_contexts.append(make_snowplow_context(schema, data))

    # add location_stack, but only if there's at least 1 item in it
    schema = f'{config.schema_objectiv_location_stack}/jsonschema/{version}'
    location_stack = {'location_stack': [filter_dict(v, ['_types']) for i, v in enumerate(event['location_stack'])]}
    if len(location_stack['location_stack']) > 0:
        self_describing_contexts.append(make_snowplow_context(schema, location_stack))

    # original format
    # Uncomment these lines to also send the original event / structure
    #
    # schema = config.schema_objectiv_taxonomy
    # _event = {'event_id' if k == 'id' else k: v for k, v in event.items()}
    # try:
    #     cookie_context = get_context(event, 'CookieIdContext')
    # except ValueError:
    #     cookie_context = {}
    # _event['cookie_id'] = cookie_context.get('cookie_id', '')
    # self_describing_contexts.append(make_snowplow_context(schema, _event))

    snowplow_contexts_schema = config.schema_contexts
    custom_context = {
        'schema': snowplow_contexts_schema,
        'data': self_describing_contexts
    }
    custom_context_json = json.dumps(custom_context)
    return str(base64.b64encode(custom_context_json.encode('UTF-8')), 'UTF-8')


def make_snowplow_context(schema: str, data: Union[Dict, List]) -> Dict:
    return {
        'schema': schema,
        'data': data
    }


def objectiv_event_to_snowplow_payload(event: EventData, config: SnowplowConfig) -> CollectorPayload:
    """
    Transform Objectiv event to Snowplow Collector Payload object:
    - Map Objectiv event properties onto the tracker protocol(using a structured event) / payload
    - Encode Objectiv event contexts onto custom contexts
    :param event: EventData
    :param config: SnowplowConfig
    :return: CollectorPayload
    """
    snowplow_payload_data_schema = config.schema_payload_data
    snowplow_collector_payload_schema = config.schema_collector_payload

    try:
        http_context = get_context(event, 'HttpContext')
    except ValueError:
        http_context = {}

    try:
        cookie_context = get_context(event, 'CookieIdContext')
    except ValueError:
        cookie_context = {}

    try:
        path_context = get_context(event, 'PathContext')
    except ValueError:
        path_context = {}

    try:
        application_context = get_context(event, 'ApplicationContext')
    except ValueError:
        application_context = {}
    query_string = urlparse(str(path_context.get('id', ''))).query

    snowplow_custom_contexts = make_snowplow_custom_contexts(event=event, config=config)
    collector_tstamp = event['collector_time']

    """
    Mapping of Objectiv data to Snowplow
    
    
    ## Timestamps, set by collector (as event properties)
    time            -> ttm       -> true_tstamp, derived_tstamp
    transport_time  -> stm      -> dvce_sent_tstamp
    corrected_time  -> dtm      -> dvce_created_tstamp
    collector_time  -> payload  -> collector_tstamp
    
    Additional time fields in Snowplow data are:
    etl_tstamp: timestamp for when the event was validated and enriched
    load_tstamp: timestamp for when the event was loaded by the loader
    
    ## Event properties
    event_id        -> eid      -> event_id
    _type           -> se_ac    -> se_action
    _types          -> se_ca    -> se_category
    
    ## Global context properties
    ApplicationContext.id       -> aid      -> app_id
    CookieIdContext.cookie_id   -> payload  -> network_userid 
    HttpContext.referrer        -> refr     -> page_referrer
    HttpContext.remote_address  -> ip       -> user_ipaddress
    PathContext.id              -> url      -> page_url
    
    Furthermore all global contexts are mapped as individual custom contexts, resulting in a separate column per
    global context type.
    
    The location_stack is mapped as a separate custom context, preserving the original location contexts, and the 
    order they were in when the event was constructed
    
    for more info on the Snowplow tracker format, and db fields:
    https://docs.snowplowanalytics.com/docs/collecting-data/collecting-from-own-applications/snowplow-tracker-protocol/
    https://docs.snowplowanalytics.com/docs/understanding-your-pipeline/canonical-event/#Date_time_fields
    https://snowplowanalytics.com/blog/2015/09/15/improving-snowplows-understanding-of-time/
    
    Objectiv taxonomy reference:
    https://objectiv.io/docs/taxonomy/reference
    """

    cookie_id = cookie_context.get('cookie_id', '')
    cookie_source = cookie_context.get('id', '')

    data = {
            "e": "se",  # mandatory: event type: structured event
            "p": "web",  # mandatory: platform
            "tv": "0.0.5",  # mandatory: tracker version
            "tna": "objectiv-tracker",  # tracker name
            "se_ac": event['_type'],  # structured event action -> event_type
            "se_ca": json.dumps(event.get('_types', [])),  # structured event category -> event_types
            "eid": event['id'],  # event_id / UUID
            "url": path_context.get('id', ''),  # Page URL
            "refr": http_context.get('referrer', ''),  # HTTP Referrer URL
            "cx": snowplow_custom_contexts,  # base64 encoded custom context
            "aid": application_context.get('id', ''),  # application id
            "ip": http_context.get('remote_address', ''),  # IP address
            "dtm": str(event['corrected_time']),  # Timestamp when event occurred, as recorded by client device
            "stm": str(event['transport_time']),  # Timestamp when event was sent by client device to collector
            "ttm": str(event['time']),  # User-set exact timestamp

        }
    if cookie_source == CookieIdSource.CLIENT:
        # only set domain_sessionid if we have a client_side id
        data["sid"] = cookie_id
    elif cookie_source == CookieIdSource.BACKEND:
        # Unique identifier for a user, based on a cookie from the collector, so only set if the source was a cookie
        data["nuid"] = cookie_id

    payload = {
        "schema": snowplow_payload_data_schema,
        "data": [data]
    }
    return CollectorPayload(
        schema=snowplow_collector_payload_schema,
        ipAddress=http_context.get('remote_address', ''),
        timestamp=collector_tstamp,
        encoding='UTF-8',
        collector='objectiv_collector',
        userAgent=http_context.get('user_agent', ''),
        refererUri=http_context.get('referrer', ''),
        path='/com.snowplowanalytics.snowplow/tp2',
        querystring=query_string,
        body=json.dumps(payload),
        headers=[],
        contentType='application/json',
        hostname='',
        networkUserId=cookie_id if cookie_source == CookieIdSource.BACKEND else None
    )


def payload_to_thrift(payload: CollectorPayload) -> bytes:
    """
    Generate Thrift message for payload, based on Thrift schema here:
        https://github.com/snowplow/snowplow/blob/master/2-collectors/thrift-schemas/collector-payload-1/src/main/thrift/collector-payload.thrift
    :param payload: CollectorPayload - class instance representing Thrift message
    :return: bytes - serialized string
    """

    # use memory buffer as transport layer
    trans = TTransport.TMemoryBuffer()

    # use the binary encoding protocol
    oprot = TBinaryProtocol.TBinaryProtocol(trans=trans)
    payload.write(oprot=oprot)

    return trans.getvalue()


def snowplow_schema_violation_json(payload: CollectorPayload, config: SnowplowConfig,
                                   event_error: EventError = None) -> Dict[str, Union[str, Dict]]:
    """
    Generate Snowplow schema violation JSON object
    :param payload: CollectorPayload object - representation of Event
    :param config: SnowplowConfig
    :param event_error: error for this event
    :return: Dictionary representing the schema violation
    """

    data_reports = []

    if event_error and event_error.error_info:
        for ei in event_error.error_info:
            data_reports.append({
                "message": ei.info,
                "path": '$',
                "keyword": "required",
                "targets": ["_type"]
            })

    parameters = []
    data = json.loads(payload.body)['data'][0]
    for key, value in data.items():
        parameters.append({
            "name": key,
            "value": value[:512]
        })

    ts_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    return {
        "schema": config.schema_schema_violations,
        # Information regarding the schema violations
        "data": {
            #   "required": [ "failure", "payload", "processor" ],
            "failure": {
                # Timestamp at which the failure occurred --> 2022-03-11T09:37:47.093932Z
                "timestamp": datetime.now().strftime(ts_format),
                # List of failure messages associated with the tracker protocol violations
                "messages": [{
                    "schemaKey": config.schema_objectiv_taxonomy,
                    "error": {
                        "error": "ValidationError",
                        "dataReports": data_reports
                        }
                    }
                ]
            },
            #
            "payload": {
                # The raw event extracted from collector payload
                # "required": [ "vendor", "version", "loaderName", "encoding" ]
                "raw": {
                    # Vendor of the adapter that processed this payload, (com.snowplowanalytics.snowplow)
                    "vendor": 'io.objectiv',
                    # Version of the adapter that processed this payload (tp2)
                    "version": '1',

                    "loaderName": 'objectiv_collector',
                    # Encoding of the collector payload
                    "encoding": payload.encoding,
                    # Query string of the collector payload containing this event
                    "parameters": parameters,
                    # Content type of the payload as detected by the collector
                    "contentType": payload.contentType,
                    "headers": payload.headers,
                    "ipAddress": payload.ipAddress,
                    "refererUri": payload.refererUri,
                    "timestamp": datetime.fromtimestamp(payload.timestamp/1000).strftime(ts_format),
                    "useragent": payload.userAgent,
                    "userId": payload.networkUserId
                }
            },
            # Information about the piece of software responsible for the creation of schema violations
            "processor": {
                # Artifact responsible for the creation of schema violations
                "artifact": 'objectiv-collector',
                # Version of the artifact responsible for the creation of schema violations
                "version": "0.0.1"
            }
        }
    }


def prepare_event_for_snowplow_pipeline(event: EventData,
                                        good: bool,
                                        config: SnowplowConfig,
                                        event_errors: List[EventError] = None) -> bytes:
    """
    Transform event into data suitable for writing to the Snowplow Pipeline. If the event is "good" this means a
    CollectorPayload object, binary-encoded using Thrift. If it's a bad event, it's transformed to a JSON-based schema
    violation.
    :param event: EventData
    :param good: bool - True if these events should go to the "good" channel
    :param config: SnowplowConfig
    :param event_errors: list of EventError
    :return: bytes object to be ingested by Snowplow pipeline
    """
    payload: CollectorPayload = objectiv_event_to_snowplow_payload(event=event, config=config)
    if good:
        data = payload_to_thrift(payload=payload)
    else:
        event_error = None
        # try to find errors for the current event_id
        if event_errors:
            for ee in event_errors:
                if ee.event_id == event['id']:
                    event_error = ee
        failed_event = snowplow_schema_violation_json(payload=payload, config=config, event_error=event_error)

        # serialize (json) and encode to bytestring for publishing
        data = json.dumps(failed_event, separators=(',', ':')).encode('utf-8')

    return data


def write_data_to_gcp_pubsub(events: EventDataList, config: SnowplowConfig, good: bool = True,
                             event_errors: List[EventError] = None) -> List:
    """
    Write provided list of events to the Snowplow GCP pipeline, using GCP PubSub
    :param events: EventDataList - List of EventData
    :param config:  SnowplowConfig
    :param good: bool - True if these events should go to the "good" channel
    :param event_errors: list of EventErrors
    :return:
    """

    project = config.gcp_project
    if good:
        # good events get sent to the raw topic, which means they get processed by snowplow's enrichment
        topic = config.gcp_pubsub_topic_raw
    else:
        # not ok events get sent to the bad topic
        topic = config.gcp_pubsub_topic_bad

    topic_path = f'projects/{project}/topics/{topic}'

    pubsub_futures = []
    for event in events:
        data = prepare_event_for_snowplow_pipeline(event=event, good=good, event_errors=event_errors, config=config)

        try:
            pubsub_future = gcp_publisher.publish(topic_path, data=data)
            pubsub_futures.append(pubsub_future)

        except NotFound as e:
            print(f'PubSub topic {topic} could not be found! {e}')

    return pubsub_futures


def write_data_to_aws_pipeline(events: EventDataList, config: SnowplowConfig,
                               good: bool = True,
                               event_errors: List[EventError] = None) -> None:
    """
    Write provided list of events to Snowplow AWS pipeline, either directly to Kinesis, or to SQS
    :param events: EventDataList - List of EventData
    :param config:  SnowplowConfig
    :param good: bool - True if these events should go to the "good" channel
    :param event_errors: list of EventErrors
    :return:
    """

    if good:
        # good events get sent to the raw topic, which means they get processed by snowplow's enrichment
        stream_name = config.aws_message_topic_raw

        # config determines whether we use sqs for raw events
        client_type = config.aws_message_raw_type
    else:
        stream_name = config.aws_message_topic_bad
        # the bad stream always goes to kinesis
        client_type = 'kinesis'

    if client_type == 'kinesis':
        client = boto3.client('kinesis')
    else:
        client = boto3.client('sqs')

    for event in events:
        data = prepare_event_for_snowplow_pipeline(event=event, good=good, event_errors=event_errors, config=config)

        if client_type == 'kinesis':
            try:
                client.put_record(
                    StreamName=stream_name,
                    Data=data,
                    PartitionKey='event_id')
            except client.exceptions.ProvisionedThroughputExceededException as e:
                print(f'Could not deliver event to Kinesis: throughput exceeded in {stream_name}: {e}')
            except botocore.exceptions.ClientError as e:
                print(f'Exception sending event to Kinesis ({stream_name}: {e}')

        elif client_type == 'sqs':
            # sqs doesn't support binary payloads, so in this case we base64 encode
            payload = str(base64.b64encode(data), 'UTF-8')

            try:
                client.send_message(QueueUrl=stream_name,
                                    MessageBody=payload,
                                    MessageAttributes={
                                        #  The sqs message attribute that will be used to set the kinesis partition key
                                        'kinesisKey': {
                                            'StringValue': 'event_id',
                                            'DataType': 'String'
                                        }
                                    })
            except client.exceptions.InvalidMessageContents as e:
                print(f'Failed to deliver event to SQS: Invalid Message Contents ({stream_name}: {e}')
            except botocore.exceptions.ClientError as e:
                print(f'Failed to deliver event to SQS ({stream_name}: {e}')

        else:
            # this should never happen
            raise ValueError(f'Unknown Client-Type: {client_type}')

