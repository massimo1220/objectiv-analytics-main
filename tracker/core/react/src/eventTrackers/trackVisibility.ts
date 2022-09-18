/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeHiddenEvent, makeVisibleEvent } from '@objectiv/tracker-core';
import { EventTrackerParameters } from '../types';

/**
 * The parameters of `trackVisibility`. Has one extra attribute, `isVisible`, as mandatory parameter.
 */
export type TrackVisibilityParameters = EventTrackerParameters & {
  /**
   * Determines whether a VisibleEvent or a HiddenEvent is tracked
   */
  isVisible: boolean;
};

/**
 * Factors either a VisibleEvent or a HiddenEvent, depending on the given `isVisible` parameter, and
 * hands it over to the given `tracker` via its `trackEvent` method.
 */
export const trackVisibility = ({
  tracker,
  isVisible,
  locationStack,
  globalContexts,
  options,
}: TrackVisibilityParameters) => {
  const extraContexts = { location_stack: locationStack, global_contexts: globalContexts };

  return tracker.trackEvent(isVisible ? makeVisibleEvent(extraContexts) : makeHiddenEvent(extraContexts), options);
};
