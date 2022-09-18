/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TagLocationAttributes } from './TagLocationAttributes';

/**
 * The parameters of `tagChild`
 */
export type ChildrenTaggingQuery = {
  queryAll: string;
  tagAs?: TagLocationAttributes;
};
