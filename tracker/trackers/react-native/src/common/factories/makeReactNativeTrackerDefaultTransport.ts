/*
 * Copyright 2022 Objectiv B.V.
 */

import { TrackerTransportInterface, TrackerTransportRetry } from '@objectiv/tracker-core';
import { FetchTransport } from '@objectiv/transport-fetch';
import { ReactNativeTrackerConfig } from '../../ReactNativeTracker';

/**
 * A factory to create the default Transport of React Native Tracker.
 */
export const makeReactNativeTrackerDefaultTransport = (
  trackerConfig: ReactNativeTrackerConfig
): TrackerTransportInterface =>
  new TrackerTransportRetry({
    transport: new FetchTransport({ endpoint: trackerConfig.endpoint }),
  });
