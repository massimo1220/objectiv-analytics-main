/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { ValidChildrenTaggingQuery } from '../../definitions/ValidChildrenTaggingQuery';
import { isValidChildrenTaggingQuery } from '../guards/isValidChildrenTaggingQuery';
import { parseJson } from './parseJson';

/**
 * ChildrenTaggingAttribute parser
 */
export const parseTagChildren = (stringifiedChildrenTaggingAttribute: string | null): ValidChildrenTaggingQuery[] => {
  if (stringifiedChildrenTaggingAttribute === null) {
    throw new Error('Received `null` while attempting to parse Children Tagging Attribute');
  }

  if (typeof stringifiedChildrenTaggingAttribute !== 'string') {
    throw new Error('Children Tagging Attribute must be a string');
  }

  const childrenTaggingAttribute = parseJson(stringifiedChildrenTaggingAttribute);

  if (!Array.isArray(childrenTaggingAttribute)) {
    throw new Error('Parsed Children Tagging Attribute is not an array');
  }

  childrenTaggingAttribute.forEach((childrenTaggingQuery) => {
    if (!isValidChildrenTaggingQuery(childrenTaggingQuery)) {
      throw new Error(`Invalid children tagging parameters: ${JSON.stringify(childrenTaggingAttribute)}`);
    }
  });

  return childrenTaggingAttribute;
};
