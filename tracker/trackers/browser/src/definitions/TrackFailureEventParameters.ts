/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { NonInteractiveEventTrackerParameters } from './NonInteractiveEventTrackerParameters';

/**
 * trackFailureEvent has an extra attribute, `message`, as mandatory parameter.
 */
export type TrackFailureEventParameters = NonInteractiveEventTrackerParameters & { message: string };
