/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { NonEmptyArray } from './helpers';
import { TrackerEvent } from './TrackerEvent';

/**
 * Our Tracker Queue Store generic interface.
 */
export interface TrackerQueueStoreInterface {
  /**
   * A name describing the Queue Store implementation for debugging purposes
   */
  readonly queueStoreName: string;

  /**
   * How many TrackerEvents are in the store
   */
  length: number;

  /**
   * Read Events from the store, if `size` is omitted all TrackerEvents will be returned
   */
  read(size?: number, filterPredicate?: (event: TrackerEvent) => boolean): Promise<TrackerEvent[]>;

  /**
   * Write Events to the store
   */
  write(...args: NonEmptyArray<TrackerEvent>): Promise<any>;

  /**
   * Delete TrackerEvents from the store by id
   */
  delete(TrackerEventIds: string[]): Promise<any>;

  /**
   * Delete all TrackerEvents from the store
   */
  clear(): Promise<any>;
}
