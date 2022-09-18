/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { FlushQueueOptions } from './FlushQueueOptions';
import { WaitForQueueOptions } from './WaitForQueueOptions';

/**
 * The Options attribute of the TrackClicks TaggingAttribute
 */
export type TrackClicksOptions =
  | undefined
  | {
      waitForQueue?: WaitForQueueOptions;
      flushQueue?: FlushQueueOptions;
    };
