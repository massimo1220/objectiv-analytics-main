/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { FlushQueueOptions } from './FlushQueueOptions';

/**
 * WaitUntilTracked Options for TrackClick TaggingAttribute
 */
export type WaitUntilTrackedOptions = {
  intervalMs?: number;
  timeoutMs?: number;
  flushQueue?: FlushQueueOptions;
};
