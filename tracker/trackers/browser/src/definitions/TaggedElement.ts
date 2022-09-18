/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TaggableElement } from './TaggableElement';
import { TagLocationAttributes } from './TagLocationAttributes';

/**
 * A TaggedElement is a TaggableElement already decorated with our LocationTaggingAttributes
 */
export type TaggedElement = TaggableElement & TagLocationAttributes;
