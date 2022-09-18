/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TagLocationParameters } from '../../definitions/TagLocationParameters';
import { isLocationContext } from './isLocationContext';
import { isTagLocationOptions } from './isTagLocationOptions';

/**
 * A type guard to determine if the given object is a TagLocationParameters.
 */
export const isTagLocationParameters = (object: Partial<TagLocationParameters>): object is TagLocationParameters => {
  if (typeof object !== 'object' || object === null) {
    return false;
  }

  if (!object.hasOwnProperty('instance')) {
    return false;
  }

  if (object.instance && !isLocationContext(object.instance)) {
    return false;
  }

  if (object.options && !isTagLocationOptions(object.options)) {
    return false;
  }

  return true;
};
