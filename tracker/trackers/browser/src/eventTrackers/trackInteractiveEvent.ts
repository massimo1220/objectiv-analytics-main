/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeInteractiveEvent } from '@objectiv/tracker-core';
import { InteractiveEventTrackerParameters } from '../definitions/InteractiveEventTrackerParameters';
import { trackEvent } from './trackEvent';

/**
 * trackInteractiveEvent is a shorthand for trackEvent. It eases triggering InteractiveEvent programmatically.
 */
export const trackInteractiveEvent = ({
  element,
  locationStack,
  globalContexts,
  tracker,
  onError,
}: InteractiveEventTrackerParameters) => {
  return trackEvent({
    event: makeInteractiveEvent({ location_stack: locationStack, global_contexts: globalContexts }),
    element,
    tracker,
    onError,
  });
};
