/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { BrowserTracker } from '../BrowserTracker';
import { trackerErrorHandler } from '../common/trackerErrorHandler';
import { TaggingAttribute } from '../definitions/TaggingAttribute';
import { trackRemovedElement } from './trackRemovedElement';

/**
 * Invokes `trackRemovedElement` for given node and all of its children if they have the `elementId` Tagging Attribute.
 */
export const trackRemovedElements = (element: Element, tracker: BrowserTracker) => {
  try {
    const elements = element.querySelectorAll(`[${TaggingAttribute.elementId}]`);
    [element, ...Array.from(elements)].forEach((element) => trackRemovedElement(element, tracker));
  } catch (error) {
    trackerErrorHandler(error);
  }
};
