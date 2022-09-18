"""
Copyright 2021 Objectiv B.V.
"""
from typing import Optional, List, cast

from objectiv_backend.common.types import EventData, ContextData, ContextType
from objectiv_backend.schema.schema import AbstractGlobalContext


def get_optional_context(event: EventData, context_type: ContextType) -> Optional[ContextData]:
    """ Get the first Context of the given type, or None if there is none. """
    result = get_contexts(event=event, context_type=context_type)
    if not result:
        return None
    return result[0]


def get_context(event: EventData, context_type: ContextType) -> ContextData:
    """ Get the first Context of the given type. """
    result = get_contexts(event=event, context_type=context_type)
    if not result:
        raise ValueError(f'context-type {context_type} not present in event. data: {event}')
    return result[0]


def get_contexts(event: EventData, context_type: ContextType) -> List[ContextData]:
    """ Given all the Contexts of the given type."""
    contexts = get_global_contexts(event) + get_location_stack(event)
    result = []
    for context in contexts:
        _contexts_types = cast(List[ContextType], context.get("_types", []))
        if context.get("_type") == context_type or context_type in _contexts_types:
            result.append(context)
    return result


def remove_global_contexts(event: EventData, context_type: ContextType):
    """
    Remove all instances of context_type from global contexts
    :param event:  EventData
    :param context_type: name of context to remove
    :return: event with global context(s) matching context_type, if any, removed
    """
    for index, context in enumerate(event['global_contexts']):
        if context.get('_type') == context_type:
            del event['global_contexts'][index]
    return event


def get_global_contexts(event: EventData) -> List[ContextData]:
    """ Given an event, return all global contexts (if any)."""
    return event.get("global_contexts", [])


def get_location_stack(event: EventData) -> List[ContextData]:
    """ Given an event, return the location stack (location contexts)."""
    return event.get("location_stack", [])


def add_global_context_to_event(event: EventData, context: AbstractGlobalContext) -> EventData:
    """ Add the global context to the event. Returns the modified event """
    event['global_contexts'].append(context)
    return event

