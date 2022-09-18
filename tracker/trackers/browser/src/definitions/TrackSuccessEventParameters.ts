/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { NonInteractiveEventTrackerParameters } from './NonInteractiveEventTrackerParameters';

/**
 * trackSuccessEvent has an extra attribute, `message`, as mandatory parameter.
 */
export type TrackSuccessEventParameters = NonInteractiveEventTrackerParameters & { message: string };
