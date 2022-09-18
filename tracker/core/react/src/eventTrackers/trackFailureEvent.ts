/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeFailureEvent } from '@objectiv/tracker-core';
import { EventTrackerParameters } from '../types';

/**
 * The parameters of trackFailureEvent. Has one extra attribute, `message`, as mandatory parameter.
 */
export type FailureEventTrackerParameters = EventTrackerParameters & {
  /**
   * The failure message or error code.
   */
  message: string;
};

/**
 * Factors an FailureEvent and hands it over to the given `tracker` via its `trackEvent` method.
 */
export const trackFailureEvent = ({
  message,
  tracker,
  locationStack,
  globalContexts,
  options,
}: FailureEventTrackerParameters) =>
  tracker.trackEvent(
    makeFailureEvent({ message, location_stack: locationStack, global_contexts: globalContexts }),
    options
  );
