/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { ChildrenTaggingQueries } from '../../definitions/ChildrenTaggingQueries';
import { isValidChildrenTaggingQuery } from '../guards/isValidChildrenTaggingQuery';

/**
 * ChildrenTaggingAttribute stringifier
 */
export const stringifyTagChildren = (queries: ChildrenTaggingQueries) => {
  queries.forEach((childrenTaggingQuery) => {
    if (!isValidChildrenTaggingQuery(childrenTaggingQuery)) {
      throw new Error(`Invalid children tagging parameters: ${JSON.stringify(queries)}`);
    }
  });

  return JSON.stringify(queries);
};
