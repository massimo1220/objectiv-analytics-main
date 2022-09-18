/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeHiddenEvent } from '@objectiv/tracker-core';
import { InteractiveEventTrackerParameters } from '../definitions/InteractiveEventTrackerParameters';
import { trackEvent } from './trackEvent';

/**
 * trackHiddenEvent is a shorthand for trackEvent. It eases triggering HiddenEvent programmatically.
 */
export const trackHiddenEvent = ({
  element,
  locationStack,
  globalContexts,
  tracker,
  onError,
}: InteractiveEventTrackerParameters) => {
  return trackEvent({
    event: makeHiddenEvent({ location_stack: locationStack, global_contexts: globalContexts }),
    element,
    tracker,
    onError,
  });
};
