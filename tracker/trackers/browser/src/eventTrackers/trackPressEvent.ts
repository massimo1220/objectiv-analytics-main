/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makePressEvent } from '@objectiv/tracker-core';
import { InteractiveEventTrackerParameters } from '../definitions/InteractiveEventTrackerParameters';
import { trackEvent } from './trackEvent';

/**
 * trackPressEvent is a shorthand for trackEvent. It eases triggering PressEvent programmatically.
 */
export const trackPressEvent = ({
  element,
  locationStack,
  globalContexts,
  tracker,
  onError,
}: InteractiveEventTrackerParameters) => {
  return trackEvent({
    event: makePressEvent({ location_stack: locationStack, global_contexts: globalContexts }),
    element,
    tracker,
    onError,
  });
};
