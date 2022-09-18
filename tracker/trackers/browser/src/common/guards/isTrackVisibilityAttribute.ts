/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TrackVisibilityAttribute } from '../../definitions/TrackVisibilityAttribute';

/**
 * A type guard to determine if the given object is a TrackVisibilityAttribute.
 */
export const isTrackVisibilityAttribute = (
  attribute: Partial<TrackVisibilityAttribute>
): attribute is TrackVisibilityAttribute => {
  if (typeof attribute !== 'boolean' && typeof attribute !== 'object') {
    return false;
  }

  if (typeof attribute === 'boolean') {
    return true;
  }

  if (!attribute.mode) {
    return false;
  }

  if (!['auto', 'manual'].includes(attribute.mode)) {
    return false;
  }

  if (attribute.mode === 'auto' && attribute.hasOwnProperty('isVisible')) {
    return false;
  }

  if (attribute.mode === 'manual' && !attribute.hasOwnProperty('isVisible')) {
    return false;
  }

  if (attribute.mode === 'manual' && typeof attribute.isVisible !== 'boolean') {
    return false;
  }

  return true;
};
