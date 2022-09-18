/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { ValidateAttribute } from '../../definitions/ValidateAttribute';

/**
 * A type guard to determine if the given object is a ValidateAttribute.
 */
export const isValidateAttribute = (object: Partial<ValidateAttribute>): object is ValidateAttribute => {
  if (typeof object !== 'object' || object === null) {
    return false;
  }

  if (!object.hasOwnProperty('locationUniqueness')) {
    return false;
  }

  if (typeof object.locationUniqueness !== 'boolean') {
    return false;
  }

  return true;
};
