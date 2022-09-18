/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TagLocationOptions } from './TagLocationOptions';
import { TrackerErrorHandlerCallback } from './TrackerErrorHandlerCallback';

/**
 * LocationTaggers are shorthands around tagLocation.
 */
export type LocationTaggerParameters = {
  id: string;
  options?: TagLocationOptions;
  onError?: TrackerErrorHandlerCallback;
};
