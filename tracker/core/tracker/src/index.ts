/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { generateGUID } from './helpers';
import { TrackerGlobalsInterface } from './TrackerGlobalsInterface';

declare global {
  var objectiv: TrackerGlobalsInterface;
}
globalThis.objectiv = globalThis.objectiv ?? {};

/**
 * Set package version in globals
 */
import pkg from '../package.json';
globalThis.objectiv.versions = globalThis.objectiv.versions ?? new Map();
globalThis.objectiv.versions.set(pkg.name, pkg.version);

/**
 * Create a client session. This can be used to detect whether a user deleted its cookies in the middle of a session.
 */
globalThis.objectiv.clientSessionId = generateGUID();

export * from './generated/ContextFactories';
export * from './generated/ContextNames';
export * from './generated/EventFactories';
export * from './generated/EventNames';

export * from './cleanObjectFromInternalProperties';
export * from './Context';
export * from './ContextValidationRules';
export * from './ErrorMessages';
export * from './EventRecorderInterface';
export * from './helpers';
export * from './isAbstractContext';
export * from './isContextEqual';
export * from './LocationTreeInterface';
export * from './RecordedEventsInterface';
export * from './Tracker';
export * from './TrackerConsoleInterface';
export * from './TrackerDeveloperToolsInterface';
export * from './TrackerEvent';
export * from './TrackerPlatform';
export * from './TrackerPluginInterface';
export * from './TrackerPluginLifecycleInterface';
export * from './TrackerPlugins';
export * from './TrackerQueue';
export * from './TrackerQueueInterface';
export * from './TrackerQueueMemoryStore';
export * from './TrackerQueueStoreInterface';
export * from './TrackerRepository';
export * from './TrackerRepositoryInterface';
export * from './TrackerTransportGroup';
export * from './TrackerTransportInterface';
export * from './TrackerTransportRetry';
export * from './TrackerTransportRetryAttempt';
export * from './TrackerTransportSwitch';
export * from './TrackerValidationRuleInterface';
export * from './TrackerValidationLifecycleInterface';
export * from './uuidv4';
