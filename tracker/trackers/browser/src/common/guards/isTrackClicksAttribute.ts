/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TrackClicksAttribute } from '../../definitions/TrackClicksAttribute';
import { isWaitUntilTrackedOptions } from './isWaitUntilTrackedOptions';

/**
 * A type guard to determine if the given object is TrackClicksAttribute.
 */
export const isTrackClicksAttribute = (attribute: Partial<TrackClicksAttribute>): attribute is TrackClicksAttribute => {
  if (typeof attribute !== 'boolean' && typeof attribute !== 'object') {
    return false;
  }

  if (attribute === null) {
    return false;
  }

  if (
    typeof attribute === 'object' &&
    attribute.waitUntilTracked !== true &&
    typeof attribute.waitUntilTracked !== 'object'
  ) {
    return false;
  }

  if (typeof attribute === 'object' && typeof attribute.waitUntilTracked === 'object') {
    return isWaitUntilTrackedOptions(attribute.waitUntilTracked);
  }

  return true;
};
