/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { isLocationContext } from '../guards/isLocationContext';
import { parseJson } from './parseJson';

/**
 * LocationContexts parser
 */
export const parseLocationContext = (stringifiedContext: string | null) => {
  const locationContext = parseJson(stringifiedContext);

  if (!isLocationContext(locationContext)) {
    throw new Error(`LocationContext is not valid: ${JSON.stringify(stringifiedContext)}`);
  }

  return locationContext;
};
