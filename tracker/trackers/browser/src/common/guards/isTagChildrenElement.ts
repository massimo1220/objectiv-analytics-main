/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { GuardableElement } from '../../definitions/GuardableElement';
import { TagChildrenElement } from '../../definitions/TagChildrenElement';
import { TaggingAttribute } from '../../definitions/TaggingAttribute';
import { isTaggableElement } from './isTaggableElement';

/**
 * A type guard to determine if the given Element is a TaggableElement decorated with ChildrenLocationTaggingAttributes.
 */
export const isTagChildrenElement = (element: GuardableElement): element is TagChildrenElement =>
  isTaggableElement(element) && element.hasAttribute(TaggingAttribute.tagChildren);
