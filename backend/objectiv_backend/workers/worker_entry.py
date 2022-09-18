"""
Copyright 2021 Objectiv B.V.
"""
import sys
import time
from typing import List, Tuple

from objectiv_backend.common.config import WORKER_BATCH_SIZE, get_collector_config
from objectiv_backend.schema.hydrate_events import hydrate_types_into_event
from objectiv_backend.schema.validate_events import validate_event_adheres_to_schema, validate_event_time, EventError
from objectiv_backend.workers.pg_queues import PostgresQueues, ProcessingStage
from objectiv_backend.workers.pg_storage import insert_events_into_nok_data
from objectiv_backend.workers.util import worker_main
from objectiv_backend.common.types import EventDataList


def main_entry(connection) -> int:
    """
    Pick events from the entry queue and insert them into the finalize queue.
    :return number of processed events
    """
    with connection:
        pg_queues = PostgresQueues(connection=connection)
        events: EventDataList = pg_queues.get_events(queue=ProcessingStage.ENTRY,
                                                     max_items=WORKER_BATCH_SIZE)
        print(f'event-ids: {sorted(event["id"] for event in events)}')

        ok_events, nok_events, event_errors = process_events_entry(events)
        # ok_events continue on the happy path
        # nok_events failed to validate and are written to the nok_data table
        pg_queues.put_events(queue=ProcessingStage.FINALIZE, events=ok_events)
        insert_events_into_nok_data(connection=connection, events=nok_events)
    return len(events)


def process_events_entry(events: EventDataList, current_millis: int = 0) -> \
        Tuple[EventDataList, EventDataList, List[EventError]]:
    """
    Two step processing of events:
    1) Modify events: hydrate all parent types of both the event and contexts into the event
    2) Split event list on events that pass validation and those that don't

    :param events: List of events. validate_structure_event_list() must pass on this list.
    :param current_millis: (current) timestamp to compare events with
    :return: tuple with three lists. Both event lists have the hydrated types.
        1) ok events: events that passed validation
        2) not-ok events: events that didn't pass validation
        3) list of errors per event
    """
    ok_events: EventDataList = []
    nok_events: EventDataList = []
    event_errors = []
    event_schema = get_collector_config().event_schema

    if current_millis == 0:
        current_millis = round(time.time() * 1000)

    for event in events:

        error_info = \
            validate_event_adheres_to_schema(event_schema=event_schema, event=event) + \
            validate_event_time(event=event, current_millis=current_millis)

        if error_info:
            print(f"error, event_id: {event['id']}, errors: {[ei.info for ei in error_info]}")
            nok_events.append(event)
            event_errors.append(EventError(event_id=event['id'], error_info=error_info))
        else:
            event = hydrate_types_into_event(event_schema=event_schema, event=event)
            ok_events.append(event)
    return ok_events, nok_events, event_errors


if __name__ == '__main__':
    _loop = sys.argv[1:2] == ['--loop']
    worker_main(function=main_entry, loop=_loop)
