/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { ContextsConfig } from './Context';
import { TrackerInterface } from './Tracker';

/**
 * All possible lifecycle methods of a TrackerPlugin.
 */
export interface TrackerPluginLifecycleInterface {
  /**
   * Executed when the Tracker initializes.
   * Useful to factor Contexts that will not change during this tracking session.
   */
  initialize?: (tracker: TrackerInterface) => void;

  /**
   * Executed before the TrackerEvent is validated and handed over to the TrackerTransport.
   * Useful to factor Contexts that may have changed from the last TrackerEvent tracking. Eg: URL, Time, User, etc
   */
  enrich?: (contexts: Required<ContextsConfig>) => void;
}
