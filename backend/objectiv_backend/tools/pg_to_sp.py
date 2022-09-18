from objectiv_backend.common.config import SnowplowConfig, get_collector_config
from objectiv_backend.common.db import get_db_connection
from objectiv_backend.snowplow.snowplow_helper import write_data_to_gcp_pubsub, write_data_to_aws_pipeline
import psycopg2.extras
from concurrent import futures

"""
Script to migrate / import objectiv events, using a Postgres database as source, and Snowplow GCP/AWS pipelines
as target. The basic process:
1. get desired events from PG db
2. iterate over batch of rows, and add some timestamp information
3. call gcp and/or aws methods if enabled.

NOTE: as PG has a primary key on event_id, this means there are no duplicate events in PG, and as such duplicate events
will not be migrated. In normal operation, this is not the case.

NOTE: This only migrates "good" events, it does not process the `nok_data` table.

Timestamps:

For this migration, we use the event['time'] parameter for all timestamps, as that is the only one we have. By setting
it for `transport_time` and `corrected_time` we force the SP enrich process to use it wherever possible to stay as
close to the original data as we can.

This means that the following columns end up with the original event['time'] value (which was corrected by the Objectiv
Collector):
- collector_tstamp
- dvce_created_tstamp
- dvce_sent_tstamp
- derived_tstamp
- true_tstamp
- load_tstamp 

However, there is a column that we cannot set from here: `etl_tstamp`, this is set by the enrich process to the current
time, which means the moment of the migration.

See: https://docs.snowplowanalytics.com/docs/understanding-your-pipeline/canonical-event/#Date_time_fields for more info
on the specifics of timestamps in Snowplow data.

"""


# use backend / collector config to determine what db / PubSub / Kinesis instances to use
output_config = get_collector_config().output
if output_config.snowplow:
    snowplow_config: SnowplowConfig = output_config.snowplow
else:
    print('Snowplow pipeline not configured')
    exit(2)
# first get all events
try:
    if not output_config.postgres:
        print('Postgres not configured')
        exit(1)
    conn = get_db_connection(output_config.postgres)
    with conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Query all events since 2022-03-01, we use this cut-off to avoid importing broken/invalid events
        # due to breaking schema changes before this date. (Last one was february)
        query = f"SELECT value FROM data WHERE day >= '2022-03-01'"
        cur.execute(query)

        count = 0
        pubsub_futures = []
        while True:
            # use batches of 100, so we don't eat all memory
            rows = cur.fetchmany(100)
            if not rows:
                break
            events = []
            for row in rows:
                count += 1
                event = row['value']
                # override / set additional timestamps, so SP properly sets them, rather than using the current time
                # see: objectiv_backend/end_point/collector.py:set_time_in_events() for more info
                event['transport_time'] = row['value']['time']
                event['corrected_time'] = row['value']['time']
                event['collector_time'] = row['value']['time']
                events.append(event)

            if snowplow_config.gcp_enabled:
                pubsub_futures += write_data_to_gcp_pubsub(events=events, config=snowplow_config, good=True)

            if snowplow_config.aws_enabled:
                write_data_to_aws_pipeline(events=events, config=snowplow_config, good=True)

            # show some progress on the console after finishing a batch
            print('.', end='')

        print(f'done processing ({count} rows)')

        # wait for all PubSub futures to complete before exiting
        print('waiting for futures to complete....', end='')
        futures.wait(pubsub_futures, return_when=futures.ALL_COMPLETED)
        print('done')

except psycopg2.DatabaseError as oe:
    print(f'Error occurred in postgres: {oe}')
    exit(1)
