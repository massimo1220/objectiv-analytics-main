/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { trackerErrorHandler } from './common/trackerErrorHandler';
import { AutoTrackingState } from './mutationObserver/AutoTrackingState';

/**
 * Stops autoTracking
 */
export const stopAutoTracking = () => {
  try {
    // Nothing to do if we are not auto-tracking
    if (!AutoTrackingState.observerInstance) {
      return;
    }

    // Stop Mutation Observer
    AutoTrackingState.observerInstance.disconnect();
    AutoTrackingState.observerInstance = null;
  } catch (error) {
    trackerErrorHandler(error);
  }
};
