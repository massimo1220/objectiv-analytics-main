/*
 * Copyright 2022 Objectiv B.V.
 */

/**
 * This is the abstract parent of all Events.
 * Inheritance: AbstractEvent
 */
export interface AbstractEvent {
  /**
   * The location stack is an ordered list (stack), that contains a hierarchy of location contexts that
   *deterministically describes where an event took place from global to specific.
   *The whole stack (list) is needed to exactly pinpoint where in the UI the event originated.
   */
  location_stack: AbstractLocationContext[];

  /**
   * Global contexts add global / general information about the event. They carry information that is not
   *related to where the Event originated (location), such as device, platform or business data.
   */
  global_contexts: AbstractGlobalContext[];

  /**
   * String containing the name of the event type. (eg. ClickEvent).
   */
  _type: string;

  /**
   * Unique identifier for a specific instance of an event. Typically UUID's are a good way of
   *implementing this. On the collector side, events should be unique, this means duplicate id's result
   *in `not ok` events.
   */
  id: string;

  /**
   * Timestamp indicating when the event was generated.
   */
  time: number;
}

/**
 * AbstractContext defines the bare minimum properties for every Context. All Contexts inherit from it.
 * Inheritance: AbstractContext
 */
export interface AbstractContext {
  /**
   * A unique identifier to discriminate Context instances across Location Stacks.
   */
  __instance_id: string;

  /**
   * A unique string identifier to be combined with the Context Type (`_type`)
   *for Context instance uniqueness.
   */
  id: string;

  /**
   * A string literal used during serialization. Should always match the Context interface name.
   */
  _type: string;
}

/**
 * This is the abstract parent of all Global Contexts. Global contexts add general information to an Event.
 * Inheritance: AbstractGlobalContext -> AbstractContext
 */
export interface AbstractGlobalContext extends AbstractContext {
  __global_context: true;
}

/**
 * AbstractLocationContext are the abstract parents of all Location Contexts.
 * Location Contexts are meant to describe where an event originated from in the visual UI.
 * Inheritance: AbstractLocationContext -> AbstractContext
 */
export interface AbstractLocationContext extends AbstractContext {
  __location_context: true;
}

/**
 *
 * Inheritance: AbstractNonInteractiveEvent -> AbstractEvent
 */
export interface AbstractNonInteractiveEvent extends AbstractEvent {
  __non_interactive_event: true;
}

/**
 *
 * Inheritance: AbstractInteractiveEvent -> AbstractEvent
 */
export interface AbstractInteractiveEvent extends AbstractEvent {
  __interactive_event: true;
}

/**
 *
 * Inheritance: AbstractMediaEvent -> AbstractNonInteractiveEvent -> AbstractEvent
 */
export interface AbstractMediaEvent extends AbstractNonInteractiveEvent {
  __media_event: true;
}

/**
 *
 * Inheritance: AbstractPressableContext -> AbstractLocationContext -> AbstractContext
 */
export interface AbstractPressableContext extends AbstractLocationContext {
  __pressable_context: true;
}
