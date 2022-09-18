/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeMediaStartEvent } from '@objectiv/tracker-core';
import { InteractiveEventTrackerParameters } from '../definitions/InteractiveEventTrackerParameters';
import { trackEvent } from './trackEvent';

/**
 * trackMediaStartEvent is a shorthand for trackEvent. It eases triggering MediaStartEvent programmatically.
 */
export const trackMediaStartEvent = ({
  element,
  locationStack,
  globalContexts,
  tracker,
  onError,
}: InteractiveEventTrackerParameters) => {
  return trackEvent({
    event: makeMediaStartEvent({ location_stack: locationStack, global_contexts: globalContexts }),
    element,
    tracker,
    onError,
  });
};
