/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { GuardableElement } from '../../definitions/GuardableElement';
import { ParentTaggedElement } from '../../definitions/ParentTaggedElement';
import { TaggingAttribute } from '../../definitions/TaggingAttribute';
import { isTaggedElement } from './isTaggedElement';

/**
 * A type guard to determine if the given Element is a TaggableElement decorated with LocationTaggingAttributes.parentElementId.
 */
export const isParentTaggedElement = (element: GuardableElement): element is ParentTaggedElement =>
  isTaggedElement(element) && element.hasAttribute(TaggingAttribute.parentElementId);
