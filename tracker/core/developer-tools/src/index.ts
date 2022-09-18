/*
 * Copyright 2022 Objectiv B.V.
 */

/**
 * Set package version in globals
 */
import pkg from '../package.json';
globalThis.objectiv = globalThis.objectiv ?? {};
globalThis.objectiv.versions = globalThis.objectiv.versions ?? new Map();
globalThis.objectiv.versions.set(pkg.name, pkg.version);

import { TrackerDeveloperToolsInterface } from '@objectiv/tracker-core';
import { EventRecorder } from './EventRecorder';
import { getLocationPath } from './getLocationPath';
import { LocationTree } from './LocationTree';
import { OpenTaxonomyValidationPlugin } from './OpenTaxonomyValidationPlugin';
import { TrackerConsole } from './TrackerConsole';
import { makeLocationContextValidationRule } from './validationRules/makeLocationContextValidationRule';
import { makeMissingGlobalContextValidationRule } from './validationRules/makeMissingGlobalContextValidationRule';
import { makeUniqueGlobalContextValidationRule } from './validationRules/makeUniqueGlobalContextValidationRule';

/**
 * A global object containing all DeveloperTools
 */
const developerTools: TrackerDeveloperToolsInterface = {
  EventRecorder,
  getLocationPath,
  LocationTree,
  makeLocationContextValidationRule,
  makeMissingGlobalContextValidationRule,
  makeUniqueGlobalContextValidationRule,
  OpenTaxonomyValidationPlugin,
  TrackerConsole,
};

/**
 * Set developer tools in globals. Globals are created by Core Tracker.
 */
globalThis.objectiv.devTools = developerTools;
