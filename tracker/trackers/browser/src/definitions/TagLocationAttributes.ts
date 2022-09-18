/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TaggingAttribute } from './TaggingAttribute';

/**
 * The object that Location Taggers return, stringified
 */
export type TagLocationAttributes = {
  [TaggingAttribute.elementId]: string;
  [TaggingAttribute.parentElementId]?: string;
  [TaggingAttribute.context]: string;
  [TaggingAttribute.trackClicks]?: string;
  [TaggingAttribute.trackBlurs]?: string;
  [TaggingAttribute.trackVisibility]?: string;
  [TaggingAttribute.validate]?: string;
};
