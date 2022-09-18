/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeSuccessEvent } from '@objectiv/tracker-core';
import { trackerErrorHandler } from '../common/trackerErrorHandler';
import { TrackSuccessEventParameters } from '../definitions/TrackSuccessEventParameters';
import { trackEvent } from './trackEvent';

/**
 * trackSuccessEvent is a shorthand for trackEvent. It eases triggering SuccessEvent programmatically.
 */
export const trackSuccessEvent = (parameters: TrackSuccessEventParameters) => {
  try {
    const { message, element = document, locationStack, globalContexts, tracker } = parameters;
    return trackEvent({
      event: makeSuccessEvent({ message, location_stack: locationStack, global_contexts: globalContexts }),
      element,
      tracker,
    });
  } catch (error) {
    trackerErrorHandler(error, parameters, parameters.onError);
  }
};
