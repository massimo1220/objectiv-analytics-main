/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { LocationTaggerParameters } from '../../definitions/LocationTaggerParameters';

/**
 * A type guard to determine if the given object is a LocationTaggerParameters.
 */
export const isLocationTaggerParameters = (
  object: Partial<LocationTaggerParameters>
): object is LocationTaggerParameters => {
  if (typeof object !== 'object' || object === null) {
    return false;
  }

  if (!object.hasOwnProperty('id')) {
    return false;
  }

  if (object.id && typeof object.id !== 'string') {
    return false;
  }

  // TODO improve

  return true;
};
