/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { LocalStorageQueueStore } from '@objectiv/queue-local-storage';
import { TrackerQueue, TrackerQueueInterface, TrackerQueueMemoryStore } from '@objectiv/tracker-core';
import { ReactTrackerConfig } from '../../ReactTracker';

/**
 * A factory to create the default Queue of React Tracker.
 */
export const makeReactTrackerDefaultQueue = (trackerConfig: ReactTrackerConfig): TrackerQueueInterface => {
  const Store = typeof localStorage !== 'undefined' ? LocalStorageQueueStore : TrackerQueueMemoryStore;

  return new TrackerQueue({
    store: new Store({
      trackerId: trackerConfig.trackerId ?? trackerConfig.applicationId,
    }),
  });
};
