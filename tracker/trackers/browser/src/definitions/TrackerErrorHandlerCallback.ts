/*
 * Copyright 2021-2022 Objectiv B.V.
 */

/**
 * Generic onError callback definition used by `trackerErrorHandler`.
 */
export type TrackerErrorHandlerCallback = <T = unknown>(error: unknown, parameters?: T) => void;
