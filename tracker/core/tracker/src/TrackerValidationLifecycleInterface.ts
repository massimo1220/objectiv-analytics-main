/*
 * Copyright 2022 Objectiv B.V.
 */

import { TrackerEvent } from './TrackerEvent';

/**
 * TrackerValidationRules always define a `validate` method.
 */
export interface TrackerValidationLifecycleInterface {
  /**
   * Validation logic may be implemented via this method and may log issues to the console.
   * Called after `enrich` and before the TrackerEvent is handed over to the TrackerTransport.
   */
  validate?: (event: TrackerEvent) => void;
}
