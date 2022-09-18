/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TrackerEventAttributes } from '@objectiv/tracker-core';
import { TrackEventParameters } from '../types';
import { useTracker } from './consumers/useTracker';
import { useOnToggle } from './useOnToggle';

/**
 * The parameters of useTrackOnToggle
 */
export type TrackOnToggleHookParameters = Partial<TrackEventParameters> & {
  /**
   * A boolean variable this hook is going to be monitoring for determining when and which event to trigger
   */
  state: boolean | (() => boolean);

  /**
   * The Event to track when state changes from `false` to `true`
   */
  trueEvent: TrackerEventAttributes;

  /**
   * Optional. The Event to track when state changes from `true` to `false`
   */
  falseEvent?: TrackerEventAttributes;
};

/**
 * A variant of the trackOnChange side effect that monitors a boolean `state`, or a predicate, and runs the given
 * `trueEvent` or `maybeFalseEvent` depending on the state value.
 * `maybeFalseEvent` can be omitted, resulting in the hook using `trueEvent` for any change.
 **/
export const useTrackOnToggle = (parameters: TrackOnToggleHookParameters) => {
  const { state, trueEvent, falseEvent, tracker = useTracker(), options } = parameters;

  return useOnToggle(
    state,
    () => tracker.trackEvent(trueEvent, options),
    falseEvent ? () => tracker.trackEvent(falseEvent, options) : undefined
  );
};
