/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeMediaEvent } from '@objectiv/tracker-core';
import { InteractiveEventTrackerParameters } from '../definitions/InteractiveEventTrackerParameters';
import { trackEvent } from './trackEvent';

/**
 * trackMediaEvent is a shorthand for trackEvent. It eases triggering MediaEvent programmatically.
 */
export const trackMediaEvent = ({
  element,
  locationStack,
  globalContexts,
  tracker,
  onError,
}: InteractiveEventTrackerParameters) => {
  return trackEvent({
    event: makeMediaEvent({ location_stack: locationStack, global_contexts: globalContexts }),
    element,
    tracker,
    onError,
  });
};
