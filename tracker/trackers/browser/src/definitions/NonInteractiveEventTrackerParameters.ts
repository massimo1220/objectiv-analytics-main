/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { InteractiveEventTrackerParameters } from './InteractiveEventTrackerParameters';

/**
 * The same parameters of regular Event Trackers, but all attributes are optional.
 */
export type NonInteractiveEventTrackerParameters = Partial<InteractiveEventTrackerParameters>;
