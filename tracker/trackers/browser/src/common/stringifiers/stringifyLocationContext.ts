/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { AnyLocationContext } from '../../definitions/LocationContext';
import { isLocationContext } from '../guards/isLocationContext';
import { stringifyJson } from './stringifyJson';

/**
 * LocationContexts stringifier
 */
export const stringifyLocationContext = (contextObject: AnyLocationContext) => {
  if (!isLocationContext(contextObject)) {
    throw new Error(`Object is not a valid LocationContext: ${JSON.stringify(contextObject)}`);
  }

  return stringifyJson(contextObject);
};
