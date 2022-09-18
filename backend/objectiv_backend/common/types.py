"""
Copyright 2021 Objectiv B.V.
"""
from enum import Enum
from typing import List, Union, Dict, Any

# an event
EventData = Dict[str, Any]
# list of events
EventDataList = List[EventData]
# eventlist, as sent by the tracker (may contain additional info, like version / timestamps, etc
EventList = Dict[str, Any]
# a list of contexts
ContextData = Dict[str, Union[str, int, float]]

EventListSchema = Dict[str, Any]

EventType = str
ContextType = str


class FailureReason(Enum):
    # values match the values of the failure_reason type in the database
    FAILED_VALIDATION = 'failed validation'
    DUPLICATE = 'duplicate'


class CookieIdSource:
    BACKEND: str = 'backend'
    CLIENT: str = 'client'
