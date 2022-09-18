/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { GuardableElement } from '../../definitions/GuardableElement';
import { TaggedElement } from '../../definitions/TaggedElement';
import { TaggingAttribute } from '../../definitions/TaggingAttribute';
import { isTaggableElement } from './isTaggableElement';

/**
 * A type guard to determine if the given Element is a TaggableElement decorated with LocationTaggingAttributes.
 * Note: For performance and simplicity we only check if `context` is present. Assume all other attributes are there.
 */
export const isTaggedElement = (element: GuardableElement): element is TaggedElement =>
  isTaggableElement(element) && element.hasAttribute(TaggingAttribute.context);
