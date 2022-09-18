/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeNonInteractiveEvent } from '@objectiv/tracker-core';
import { NonInteractiveEventTrackerParameters } from '../definitions/NonInteractiveEventTrackerParameters';
import { trackEvent } from './trackEvent';

/**
 * trackNonInteractiveEvent is a shorthand for trackEvent. It eases triggering NonInteractiveEvent programmatically.
 */
export const trackNonInteractiveEvent = ({
  element,
  locationStack,
  globalContexts,
  tracker,
  onError,
}: NonInteractiveEventTrackerParameters) => {
  return trackEvent({
    event: makeNonInteractiveEvent({ location_stack: locationStack, global_contexts: globalContexts }),
    element,
    tracker,
    onError,
  });
};
