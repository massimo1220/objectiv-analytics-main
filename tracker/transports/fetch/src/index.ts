/*
 * Copyright 2021-2022 Objectiv B.V.
 */

/**
 * Set package version in globals
 */
import pkg from '../package.json';
globalThis.objectiv = globalThis.objectiv ?? {};
globalThis.objectiv.versions = globalThis.objectiv.versions ?? new Map();
globalThis.objectiv.versions.set(pkg.name, pkg.version);

export * from './defaultFetchFunction';
export * from './defaultFetchOptions';
export * from './FetchTransport';
