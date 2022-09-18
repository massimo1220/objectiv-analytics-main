/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TrackVisibilityAttribute } from '../../definitions/TrackVisibilityAttribute';
import { isTrackVisibilityAttribute } from '../guards/isTrackVisibilityAttribute';
import { stringifyJson } from './stringifyJson';

/**
 * `trackVisibility` Tagging Attribute stringifier
 */
export const stringifyTrackVisibility = (trackVisibilityAttribute: TrackVisibilityAttribute) => {
  if (!isTrackVisibilityAttribute(trackVisibilityAttribute)) {
    throw new Error(`trackVisibility is not valid, received: ${JSON.stringify(trackVisibilityAttribute)}`);
  }

  return stringifyJson(trackVisibilityAttribute);
};
