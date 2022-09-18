/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { BrowserTracker } from '../BrowserTracker';
import { parseTrackVisibility } from '../common/parsers/parseTrackVisibility';
import { trackerErrorHandler } from '../common/trackerErrorHandler';
import { TaggedElement } from '../definitions/TaggedElement';
import { TaggingAttribute } from '../definitions/TaggingAttribute';
import { trackHiddenEvent } from '../eventTrackers/trackHiddenEvent';

/**
 * Checks whether to trigger a visibility: hidden event for the given TaggedElement.
 * Hidden Events are triggered only for Elements that have their visibility manually set to not visible.
 */
export const trackVisibilityHiddenEvent = (element: TaggedElement, tracker: BrowserTracker) => {
  try {
    if (!element.hasAttribute(TaggingAttribute.trackVisibility)) {
      return;
    }
    const trackVisibility = parseTrackVisibility(element.getAttribute(TaggingAttribute.trackVisibility));
    if (trackVisibility && trackVisibility.mode === 'manual' && !trackVisibility.isVisible) {
      trackHiddenEvent({ element, tracker });
    }
  } catch (error) {
    trackerErrorHandler(error);
  }
};
