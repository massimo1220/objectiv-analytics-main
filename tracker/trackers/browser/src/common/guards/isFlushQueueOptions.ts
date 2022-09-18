/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { FlushQueueOptions } from '../../definitions/FlushQueueOptions';

/**
 * A type guard to determine if the given options is FlushQueueOptions.
 */
export const isFlushQueueOptions = (options: Partial<FlushQueueOptions>): options is FlushQueueOptions => {
  return options === true || options === false || options === 'onTimeout';
};
