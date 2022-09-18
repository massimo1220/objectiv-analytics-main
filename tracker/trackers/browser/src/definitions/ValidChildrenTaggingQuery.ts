/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TagLocationAttributes } from './TagLocationAttributes';

/**
 * The parameters of `tagChild` where `tagAs` is a valid TagLocationAttributes
 */
export type ValidChildrenTaggingQuery = {
  queryAll: string;
  tagAs: TagLocationAttributes;
};
