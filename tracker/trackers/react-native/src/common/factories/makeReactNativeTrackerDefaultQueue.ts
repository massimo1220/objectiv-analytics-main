/*
 * Copyright 2022 Objectiv B.V.
 */

import { TrackerQueue, TrackerQueueInterface, TrackerQueueMemoryStore } from '@objectiv/tracker-core';

/**
 * A factory to create the default Queue of React Native Tracker.
 * // TODO consider using Async Storage
 */
export const makeReactNativeTrackerDefaultQueue = (): TrackerQueueInterface =>
  new TrackerQueue({
    store: new TrackerQueueMemoryStore(),
  });
