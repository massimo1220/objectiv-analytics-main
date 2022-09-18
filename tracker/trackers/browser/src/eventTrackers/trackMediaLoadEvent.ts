/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeMediaLoadEvent } from '@objectiv/tracker-core';
import { InteractiveEventTrackerParameters } from '../definitions/InteractiveEventTrackerParameters';
import { trackEvent } from './trackEvent';

/**
 * trackMediaLoadEvent is a shorthand for trackEvent. It eases triggering MediaLoadEvent programmatically.
 */
export const trackMediaLoadEvent = ({
  element,
  locationStack,
  globalContexts,
  tracker,
  onError,
}: InteractiveEventTrackerParameters) => {
  return trackEvent({
    event: makeMediaLoadEvent({ location_stack: locationStack, global_contexts: globalContexts }),
    element,
    tracker,
    onError,
  });
};
