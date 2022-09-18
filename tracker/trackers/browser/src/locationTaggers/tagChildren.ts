/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { isValidChildrenTaggingQuery } from '../common/guards/isValidChildrenTaggingQuery';
import { stringifyTagChildren } from '../common/stringifiers/stringifyTagChildren';
import { trackerErrorHandler } from '../common/trackerErrorHandler';
import { ChildrenTaggingQueries } from '../definitions/ChildrenTaggingQueries';
import { TagChildrenReturnValue } from '../definitions/TagChildrenReturnValue';
import { TaggingAttribute } from '../definitions/TaggingAttribute';
import { TrackerErrorHandlerCallback } from '../definitions/TrackerErrorHandlerCallback';

/**
 * Used to decorate a TaggableElement with our Children Tagging Attributes.
 *
 * Returns an object containing the Children Tagging Attribute only.
 * This attribute is a serialized list of ChildrenTaggingQuery objects and will be parsed and executed by our Observer
 * as soon as the elements gets rendered.
 *
 * Examples
 *
 *    tagChildren([
 *      {
 *        queryAll: 'button[aria-label="Previous"]',
 *        tagAs: tagPressable({ id: 'prev', text: 'Previous' })
 *      },
 *      {
 *        queryAll: 'button[aria-label="Next"]',
 *        tagAs: tagPressable({ id: 'next', text: 'Next' })
 *      }
 *    ])
 */
export const tagChildren = (
  parameters: ChildrenTaggingQueries,
  onError?: TrackerErrorHandlerCallback
): TagChildrenReturnValue => {
  try {
    parameters.forEach((childrenTaggingQuery) => {
      if (!isValidChildrenTaggingQuery(childrenTaggingQuery)) {
        throw new Error(`Invalid children tagging parameters: ${JSON.stringify(parameters)}`);
      }
    });

    return {
      [TaggingAttribute.tagChildren]: stringifyTagChildren(parameters),
    };
  } catch (error) {
    return trackerErrorHandler(error, parameters, onError);
  }
};
