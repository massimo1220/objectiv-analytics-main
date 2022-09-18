/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { isNonEmptyArray, NonEmptyArray, TrackerTransportInterface, TransportableEvent } from '@objectiv/tracker-core';
import { defaultXHRFunction } from './defaultXHRFunction';

/**
 * The configuration of the XHRTransport class
 */
export type XHRTransportConfig = {
  /**
   * The collector endpoint URL.
   */
  endpoint?: string;

  /**
   * Optional. Override the default XMLHttpRequestFunction implementation with a custom one.
   */
  xmlHttpRequestFunction?: typeof defaultXHRFunction;
};

/**
 * A TrackerTransport based on XMLHttpRequest. Sends event to the specified Collector endpoint.
 * Optionally supports specifying a custom `xmlHttpRequestFunction`.
 */
export class XHRTransport implements TrackerTransportInterface {
  readonly endpoint?: string;
  readonly transportName = 'XHRTransport';
  readonly xmlHttpRequestFunction: typeof defaultXHRFunction;

  constructor(config: XHRTransportConfig) {
    this.endpoint = config.endpoint;
    this.xmlHttpRequestFunction = config.xmlHttpRequestFunction ?? defaultXHRFunction;
  }

  async handle(...args: NonEmptyArray<TransportableEvent>): Promise<any> {
    const events = await Promise.all(args);

    if (this.endpoint && isNonEmptyArray(events)) {
      return this.xmlHttpRequestFunction({ endpoint: this.endpoint, events });
    }
  }

  isUsable(): boolean {
    return typeof XMLHttpRequest !== 'undefined';
  }
}
