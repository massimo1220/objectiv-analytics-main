/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeInputChangeEvent } from '@objectiv/tracker-core';
import { InteractiveEventTrackerParameters } from '../definitions/InteractiveEventTrackerParameters';
import { trackEvent } from './trackEvent';

/**
 * trackInputChangeEvent is a shorthand for trackEvent. It eases triggering InputChangeEvent programmatically.
 */
export const trackInputChangeEvent = ({
  element,
  locationStack,
  globalContexts,
  tracker,
  onError,
}: InteractiveEventTrackerParameters) => {
  return trackEvent({
    event: makeInputChangeEvent({ location_stack: locationStack, global_contexts: globalContexts }),
    element,
    tracker,
    onError,
  });
};
