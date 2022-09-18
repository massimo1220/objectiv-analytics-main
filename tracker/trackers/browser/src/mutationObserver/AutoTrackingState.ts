/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { getLocationHref } from '../common/getLocationHref';

/**
 * Hold an instance of the Mutation Observer and some state for some global events, like URLs and Application Loaded.
 */
export const AutoTrackingState: {
  observerInstance: MutationObserver | null;
  applicationLoaded: boolean;
  previousURL: string | undefined;
} = {
  /**
   * Holds the instance to the Tagged Elements Mutation Observer created by `startAutoTracking`
   */
  observerInstance: null,

  /**
   * Whether we already tracked the ApplicationLoaded Event or not
   */
  applicationLoaded: false,

  /**
   * Holds the last seen URL
   */
  previousURL: getLocationHref(),
};
