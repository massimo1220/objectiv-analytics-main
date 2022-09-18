/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeVisibleEvent } from '@objectiv/tracker-core';
import { InteractiveEventTrackerParameters } from '../definitions/InteractiveEventTrackerParameters';
import { trackEvent } from './trackEvent';

/**
 * trackVisibleEvent is a shorthand for trackEvent. It eases triggering VisibleEvent programmatically.
 */
export const trackVisibleEvent = ({
  element,
  locationStack,
  globalContexts,
  tracker,
  onError,
}: InteractiveEventTrackerParameters) => {
  return trackEvent({
    event: makeVisibleEvent({ location_stack: locationStack, global_contexts: globalContexts }),
    element,
    tracker,
    onError,
  });
};
