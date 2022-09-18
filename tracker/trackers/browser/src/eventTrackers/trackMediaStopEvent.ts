/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeMediaStopEvent } from '@objectiv/tracker-core';
import { InteractiveEventTrackerParameters } from '../definitions/InteractiveEventTrackerParameters';
import { trackEvent } from './trackEvent';

/**
 * trackMediaStopEvent is a shorthand for trackEvent. It eases triggering MediaStopEvent programmatically.
 */
export const trackMediaStopEvent = ({
  element,
  locationStack,
  globalContexts,
  tracker,
  onError,
}: InteractiveEventTrackerParameters) => {
  return trackEvent({
    event: makeMediaStopEvent({ location_stack: locationStack, global_contexts: globalContexts }),
    element,
    tracker,
    onError,
  });
};
