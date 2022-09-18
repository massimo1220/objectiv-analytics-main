"""
Copyright 2021 Objectiv B.V.
"""
import sys

from objectiv_backend.common.config import WORKER_BATCH_SIZE
from objectiv_backend.common.types import EventDataList
from objectiv_backend.workers.pg_queues import PostgresQueues, ProcessingStage
from objectiv_backend.workers.pg_storage import insert_events_into_data
from objectiv_backend.workers.util import worker_main


def main_finalize(connection) -> int:
    """
    Pick events from the finalize queue, and write them to the data table.
    :return number of processed events
    """
    with connection:
        pg_queues = PostgresQueues(connection=connection)
        events: EventDataList = pg_queues.get_events(queue=ProcessingStage.FINALIZE, max_items=WORKER_BATCH_SIZE)
        print(f'event-ids: {sorted(event["id"] for event in events)}')
        insert_events_into_data(connection, events)
    return len(events)


if __name__ == '__main__':
    _loop = sys.argv[1:2] == ['--loop']
    worker_main(function=main_finalize, loop=_loop)
