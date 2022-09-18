/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import React from 'react';
import { TrackerProviderContext } from '../../common/providers/TrackerProviderContext';

/**
 * A utility hook to easily retrieve the Tracker instance from the TrackerProviderContext.
 */
export const useTracker = () => {
  const trackerProviderContext = React.useContext(TrackerProviderContext);

  if (!trackerProviderContext) {
    throw new Error(`
      Couldn't get a Tracker. 
      Is the Component in a ObjectivProvider, TrackingContextProvider or TrackerProvider?
    `);
  }

  // Return a frozen version of the actual Tracker safeguard against mutations
  return trackerProviderContext.tracker;
};
