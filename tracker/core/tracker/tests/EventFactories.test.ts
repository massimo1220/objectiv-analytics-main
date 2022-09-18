/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import {
  makeApplicationContext,
  makeApplicationLoadedEvent,
  makeContentContext,
  makeFailureEvent,
  makeHiddenEvent,
  makeInputChangeEvent,
  makeInteractiveEvent,
  makeMediaEvent,
  makeMediaLoadEvent,
  makeMediaPauseEvent,
  makeMediaStartEvent,
  makeMediaStopEvent,
  makeNonInteractiveEvent,
  makePressEvent,
  makeSuccessEvent,
  makeVisibleEvent,
} from '../src';

const contentA = makeContentContext({ id: 'A' });
const appContext = makeApplicationContext({ id: 'app' });
const customContexts = { location_stack: [contentA], global_contexts: [appContext] };

describe('Event Factories', () => {
  it('ApplicationLoadedEvent', () => {
    expect(makeApplicationLoadedEvent()).toStrictEqual({
      __non_interactive_event: true,
      _type: 'ApplicationLoadedEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeApplicationLoadedEvent(customContexts)).toStrictEqual({
      __non_interactive_event: true,
      _type: 'ApplicationLoadedEvent',
      global_contexts: [appContext],
      location_stack: [contentA],
    });
  });

  it('FailureEvent', () => {
    expect(makeFailureEvent({ message: 'ko' })).toStrictEqual({
      __non_interactive_event: true,
      _type: 'FailureEvent',
      global_contexts: [],
      location_stack: [],
      message: 'ko',
    });

    expect(makeFailureEvent({ message: 'ko', ...customContexts })).toStrictEqual({
      __non_interactive_event: true,
      _type: 'FailureEvent',
      global_contexts: [appContext],
      location_stack: [contentA],
      message: 'ko',
    });
  });

  it('HiddenEvent', () => {
    expect(makeHiddenEvent()).toStrictEqual({
      __non_interactive_event: true,
      _type: 'HiddenEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeHiddenEvent(customContexts)).toStrictEqual({
      __non_interactive_event: true,
      _type: 'HiddenEvent',
      global_contexts: [appContext],
      location_stack: [contentA],
    });
  });

  it('InputChangeEvent', () => {
    expect(makeInputChangeEvent()).toStrictEqual({
      __interactive_event: true,
      _type: 'InputChangeEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeInputChangeEvent(customContexts)).toStrictEqual({
      __interactive_event: true,
      _type: 'InputChangeEvent',
      global_contexts: [appContext],
      location_stack: [contentA],
    });
  });

  it('InteractiveEvent', () => {
    expect(makeInteractiveEvent()).toStrictEqual({
      __interactive_event: true,
      _type: 'InteractiveEvent',
      global_contexts: [],
      location_stack: [],
    });
    expect(makeInteractiveEvent(customContexts)).toStrictEqual({
      __interactive_event: true,
      _type: 'InteractiveEvent',
      global_contexts: [appContext],
      location_stack: [contentA],
    });
  });

  it('MediaEvent', () => {
    expect(makeMediaEvent()).toStrictEqual({
      __non_interactive_event: true,
      __media_event: true,
      _type: 'MediaEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeMediaEvent(customContexts)).toStrictEqual({
      __non_interactive_event: true,
      __media_event: true,
      _type: 'MediaEvent',
      global_contexts: [appContext],
      location_stack: [contentA],
    });
  });

  it('MediaLoadEvent', () => {
    expect(makeMediaLoadEvent()).toStrictEqual({
      __non_interactive_event: true,
      __media_event: true,
      _type: 'MediaLoadEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeMediaLoadEvent(customContexts)).toStrictEqual({
      __non_interactive_event: true,
      __media_event: true,
      _type: 'MediaLoadEvent',
      global_contexts: [appContext],
      location_stack: [contentA],
    });
  });

  it('MediaStartEvent', () => {
    expect(makeMediaStartEvent()).toStrictEqual({
      __non_interactive_event: true,
      __media_event: true,
      _type: 'MediaStartEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeMediaStartEvent(customContexts)).toStrictEqual({
      __non_interactive_event: true,
      __media_event: true,
      _type: 'MediaStartEvent',
      global_contexts: [appContext],
      location_stack: [contentA],
    });
  });

  it('MediaStopEvent', () => {
    expect(makeMediaStopEvent()).toStrictEqual({
      __non_interactive_event: true,
      __media_event: true,
      _type: 'MediaStopEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeMediaStopEvent(customContexts)).toStrictEqual({
      __non_interactive_event: true,
      __media_event: true,
      _type: 'MediaStopEvent',
      global_contexts: [appContext],
      location_stack: [contentA],
    });
  });

  it('MediaPauseEvent', () => {
    expect(makeMediaPauseEvent()).toStrictEqual({
      __non_interactive_event: true,
      __media_event: true,
      _type: 'MediaPauseEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeMediaPauseEvent(customContexts)).toStrictEqual({
      __non_interactive_event: true,
      __media_event: true,
      _type: 'MediaPauseEvent',
      global_contexts: [appContext],
      location_stack: [contentA],
    });
  });

  it('NonInteractiveEvent', () => {
    expect(makeNonInteractiveEvent()).toStrictEqual({
      __non_interactive_event: true,
      _type: 'NonInteractiveEvent',
      global_contexts: [],
      location_stack: [],
    });
    expect(makeNonInteractiveEvent(customContexts)).toStrictEqual({
      __non_interactive_event: true,
      _type: 'NonInteractiveEvent',
      global_contexts: [appContext],
      location_stack: [contentA],
    });
  });

  it('PressEvent', () => {
    expect(makePressEvent()).toStrictEqual({
      __interactive_event: true,
      _type: 'PressEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makePressEvent(customContexts)).toStrictEqual({
      __interactive_event: true,
      _type: 'PressEvent',
      global_contexts: [appContext],
      location_stack: [contentA],
    });
  });

  it('SuccessEvent', () => {
    expect(makeSuccessEvent({ message: 'ok' })).toStrictEqual({
      __non_interactive_event: true,
      _type: 'SuccessEvent',
      global_contexts: [],
      location_stack: [],
      message: 'ok',
    });

    expect(makeSuccessEvent({ message: 'ok', ...customContexts })).toStrictEqual({
      __non_interactive_event: true,
      _type: 'SuccessEvent',
      global_contexts: [appContext],
      location_stack: [contentA],
      message: 'ok',
    });
  });

  it('VisibleEvent', () => {
    expect(makeVisibleEvent()).toStrictEqual({
      __non_interactive_event: true,
      _type: 'VisibleEvent',
      global_contexts: [],
      location_stack: [],
    });

    expect(makeVisibleEvent(customContexts)).toStrictEqual({
      __non_interactive_event: true,
      _type: 'VisibleEvent',
      global_contexts: [appContext],
      location_stack: [contentA],
    });
  });
});
