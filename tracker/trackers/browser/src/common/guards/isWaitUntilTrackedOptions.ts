/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { WaitUntilTrackedOptions } from '../../definitions/WaitUntilTrackedOptions';
import { isFlushQueueOptions } from './isFlushQueueOptions';

/**
 * A type guard to determine if the given object is WaitUntilTrackedOptions.
 */
export const isWaitUntilTrackedOptions = (
  object: Partial<WaitUntilTrackedOptions>
): object is WaitUntilTrackedOptions => {
  if (typeof object !== 'object' || object === null) {
    return false;
  }

  if (object.intervalMs === undefined && object.timeoutMs === undefined && object.flushQueue === undefined) {
    return false;
  }

  if (object.intervalMs !== undefined && typeof object.intervalMs !== 'number') {
    return false;
  }

  if (object.timeoutMs !== undefined && typeof object.timeoutMs !== 'number') {
    return false;
  }

  if (object.flushQueue !== undefined && !isFlushQueueOptions(object.flushQueue)) {
    return false;
  }

  return true;
};
