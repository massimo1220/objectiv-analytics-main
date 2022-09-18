/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TrackerTransportInterface, TrackerTransportRetry, TrackerTransportSwitch } from '@objectiv/tracker-core';
import { FetchTransport } from '@objectiv/transport-fetch';
import { XHRTransport } from '@objectiv/transport-xhr';
import { BrowserTrackerConfig } from '../../definitions/BrowserTrackerConfig';

/**
 * A factory to create the default Transport of Browser Tracker.
 */
export const makeBrowserTrackerDefaultTransport = (trackerConfig: BrowserTrackerConfig): TrackerTransportInterface =>
  new TrackerTransportRetry({
    transport: new TrackerTransportSwitch({
      transports: [
        new FetchTransport({ endpoint: trackerConfig.endpoint }),
        new XHRTransport({ endpoint: trackerConfig.endpoint }),
      ],
    }),
  });
