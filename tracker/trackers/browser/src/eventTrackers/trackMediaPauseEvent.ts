/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeMediaPauseEvent } from '@objectiv/tracker-core';
import { InteractiveEventTrackerParameters } from '../definitions/InteractiveEventTrackerParameters';
import { trackEvent } from './trackEvent';

/**
 * trackMediaPauseEvent is a shorthand for trackEvent. It eases triggering MediaPauseEvent programmatically.
 */
export const trackMediaPauseEvent = ({
  element,
  locationStack,
  globalContexts,
  tracker,
  onError,
}: InteractiveEventTrackerParameters) => {
  return trackEvent({
    event: makeMediaPauseEvent({ location_stack: locationStack, global_contexts: globalContexts }),
    element,
    tracker,
    onError,
  });
};
