/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { AnyLocationContext } from './LocationContext';
import { TagLocationOptions } from './TagLocationOptions';
import { TrackerErrorHandlerCallback } from './TrackerErrorHandlerCallback';

/**
 * The parameters of `tagLocation` and its shorthands
 */
export type TagLocationParameters = {
  instance: AnyLocationContext;
  options?: TagLocationOptions;
  onError?: TrackerErrorHandlerCallback;
};
