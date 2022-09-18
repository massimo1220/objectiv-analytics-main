/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { ValidChildrenTaggingQuery } from '../../definitions/ValidChildrenTaggingQuery';
import { isTagLocationAttributes } from './isTagLocationAttributes';

/**
 * A type guard to determine if the given object is a TagChildrenParameters.
 */
export const isValidChildrenTaggingQuery = (
  object: Partial<ValidChildrenTaggingQuery>
): object is ValidChildrenTaggingQuery => {
  if (typeof object !== 'object' || object === null) {
    return false;
  }

  if (object.queryAll === undefined || object.tagAs === undefined) {
    return false;
  }

  if (object.queryAll !== undefined && typeof object.queryAll !== 'string') {
    return false;
  }

  if (object.tagAs !== undefined && !isTagLocationAttributes(object.tagAs)) {
    return false;
  }

  return true;
};
