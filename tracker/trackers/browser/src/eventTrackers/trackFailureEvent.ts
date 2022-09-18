/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeFailureEvent } from '@objectiv/tracker-core';
import { trackerErrorHandler } from '../common/trackerErrorHandler';
import { TrackFailureEventParameters } from '../definitions/TrackFailureEventParameters';
import { trackEvent } from './trackEvent';

/**
 * trackFailureEvent is a shorthand for trackEvent. It eases triggering FailureEvent programmatically.
 */
export const trackFailureEvent = (parameters: TrackFailureEventParameters) => {
  try {
    const { message, element = document, locationStack, globalContexts, tracker } = parameters;
    return trackEvent({
      event: makeFailureEvent({ message, location_stack: locationStack, global_contexts: globalContexts }),
      element,
      tracker,
    });
  } catch (error) {
    trackerErrorHandler(error, parameters, parameters.onError);
  }
};
