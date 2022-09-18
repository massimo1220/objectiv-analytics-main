/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TaggingAttribute } from '../../definitions/TaggingAttribute';
import { TagLocationAttributes } from '../../definitions/TagLocationAttributes';

/**
 * A type guard to determine if the given object is a isTagLocationAttributes.
 */
export const isTagLocationAttributes = (object: Partial<TagLocationAttributes>): object is TagLocationAttributes => {
  if (typeof object !== 'object' || object === null) {
    return false;
  }

  if (object[TaggingAttribute.elementId] === undefined || object[TaggingAttribute.context] === undefined) {
    return false;
  }

  return true;
};
