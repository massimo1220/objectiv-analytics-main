/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { ChildrenTaggingQuery } from '../definitions/ChildrenTaggingQuery';
import { TagChildrenReturnValue } from '../definitions/TagChildrenReturnValue';
import { TrackerErrorHandlerCallback } from '../definitions/TrackerErrorHandlerCallback';
import { tagChildren } from './tagChildren';

/**
 * Syntactic sugar to track only one child.
 *
 * Examples
 *
 *    tagChild({
 *      query: '#button1',
 *      tagAs: tagPressable({ id: 'button1', text: 'Button 1' })
 *    })
 *
 *    tagChild({
 *      query: '#button2',
 *      tagAs: tagPressable({ id: 'button2', text: 'Button 2' })
 *    })
 *
 */
export const tagChild = (
  parameters: ChildrenTaggingQuery,
  onError?: TrackerErrorHandlerCallback
): TagChildrenReturnValue => {
  return tagChildren([parameters], onError);
};
