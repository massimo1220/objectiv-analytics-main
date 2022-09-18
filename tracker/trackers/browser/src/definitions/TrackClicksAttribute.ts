/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { WaitUntilTrackedOptions } from './WaitUntilTrackedOptions';

/**
 * The definition for the `trackClicks` Tagging Attribute
 */
export type TrackClicksAttribute =
  | boolean
  | {
      waitUntilTracked: true | WaitUntilTrackedOptions;
    };
