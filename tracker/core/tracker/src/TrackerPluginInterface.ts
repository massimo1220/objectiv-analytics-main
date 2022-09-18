/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TrackerPluginLifecycleInterface } from './TrackerPluginLifecycleInterface';
import { TrackerValidationLifecycleInterface } from './TrackerValidationLifecycleInterface';

/**
 * A TrackerPlugin must define its own `pluginName` and may define TrackerPluginLifecycle callbacks.
 * It also defines a method to determine if the plugin can be used. Similarly to the Transport interface, this can
 * be used to check environment requirements, APIs availability, etc.
 */
export interface TrackerPluginInterface extends TrackerPluginLifecycleInterface, TrackerValidationLifecycleInterface {
  readonly pluginName: string;

  /**
   * Should return if the TrackerPlugin can be used. Eg: a browser based plugin may want to return `false` during SSR.
   */
  isUsable(): boolean;
}

/**
 * The TrackerPlugin constructor interface.
 */
export interface TrackerPluginConstructor {
  new (): TrackerPluginInterface;
}
