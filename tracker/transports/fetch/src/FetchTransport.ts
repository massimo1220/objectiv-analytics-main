/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { isNonEmptyArray, NonEmptyArray, TrackerTransportInterface, TransportableEvent } from '@objectiv/tracker-core';
import { defaultFetchFunction } from './defaultFetchFunction';

/**
 * The configuration of the FetchTransport class
 */
export type FetchTransportConfig = {
  /**
   * The collector endpoint URL.
   */
  endpoint?: string;

  /**
   * Optional. Override the default fetch API implementation with a custom one.
   */
  fetchFunction?: typeof defaultFetchFunction;
};

/**
 * A TrackerTransport based on Fetch API. Sends event to the specified Collector endpoint.
 * Optionally supports specifying a custom `fetchFunction`.
 */
export class FetchTransport implements TrackerTransportInterface {
  readonly endpoint?: string;
  readonly transportName = 'FetchTransport';
  readonly fetchFunction: typeof defaultFetchFunction;

  constructor(config: FetchTransportConfig) {
    this.endpoint = config.endpoint;
    this.fetchFunction = config.fetchFunction ?? defaultFetchFunction;
  }

  async handle(...args: NonEmptyArray<TransportableEvent>): Promise<Response | void> {
    const events = await Promise.all(args);

    if (this.endpoint && isNonEmptyArray(events)) {
      return this.fetchFunction({ endpoint: this.endpoint, events });
    }
  }

  isUsable(): boolean {
    return typeof fetch !== 'undefined';
  }
}
