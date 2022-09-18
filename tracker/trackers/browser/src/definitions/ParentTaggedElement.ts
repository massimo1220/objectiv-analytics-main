/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TaggableElement } from './TaggableElement';
import { TaggingAttribute } from './TaggingAttribute';
import { TagLocationAttributes } from './TagLocationAttributes';

/**
 * A ParentTaggedElement is a TaggedElement with the TaggingAttribute.parentElementId
 */
export type ParentTaggedElement = TaggableElement & Pick<TagLocationAttributes, TaggingAttribute.parentElementId>;
