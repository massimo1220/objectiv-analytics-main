/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeSuccessEvent } from '@objectiv/tracker-core';
import { EventTrackerParameters } from '../types';

/**
 * The parameters of trackSuccessEvent. Has one extra attribute, `message`, as mandatory parameter.
 */
export type SuccessEventTrackerParameters = EventTrackerParameters & {
  /**
   * The success message or status code.
   */
  message: string;
};

/**
 * Factors a SuccessEvent and hands it over to the given `tracker` via its `trackEvent` method.
 */
export const trackSuccessEvent = ({
  message,
  tracker,
  locationStack,
  globalContexts,
  options,
}: SuccessEventTrackerParameters) =>
  tracker.trackEvent(
    makeSuccessEvent({ message, location_stack: locationStack, global_contexts: globalContexts }),
    options
  );
