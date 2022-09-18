/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { trackerErrorHandler } from './common/trackerErrorHandler';
import { BrowserTrackerConfig } from './definitions/BrowserTrackerConfig';
import { TaggingAttribute } from './definitions/TaggingAttribute';
import { trackApplicationLoadedEvent } from './eventTrackers/trackApplicationLoadedEvent';
import { getTracker } from './getTracker';
import { AutoTrackingState } from './mutationObserver/AutoTrackingState';
import { makeMutationCallback } from './mutationObserver/makeMutationCallback';
import { trackNewElements } from './mutationObserver/trackNewElements';

/**
 * Initializes our automatic tracking, based on Mutation Observer.
 * Also tracks application Loaded.
 * Safe to call multiple times: it will auto-track only once.
 */
export const startAutoTracking = (options?: Pick<BrowserTrackerConfig, 'trackApplicationLoadedEvent'>) => {
  try {
    // Nothing to do if we are already auto-tracking
    if (AutoTrackingState.observerInstance) {
      return;
    }

    // Create Mutation Observer Callback
    const mutationCallback = makeMutationCallback();

    // Create Mutation Observer
    AutoTrackingState.observerInstance = new MutationObserver(mutationCallback);

    // Track existing DOM, in case our observer gets booted in an already populated DOM (SSR)
    trackNewElements(document.documentElement, getTracker());

    // Start observing DOM
    AutoTrackingState.observerInstance.observe(document, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeOldValue: true,
      attributeFilter: [TaggingAttribute.trackVisibility, TaggingAttribute.elementId],
    });

    // Track ApplicationLoaded Event - once
    if ((options?.trackApplicationLoadedEvent ?? true) && !AutoTrackingState.applicationLoaded) {
      AutoTrackingState.applicationLoaded = true;
      trackApplicationLoadedEvent({ tracker: getTracker() });
    }
  } catch (error) {
    trackerErrorHandler(error);
  }
};
