/*
 * Copyright 2022 Objectiv B.V.
 */

import {
  EventToValidate,
  GlobalContextName,
  LocationContextName,
  TrackerEvent,
  TrackerInterface,
  TrackerPluginInterface,
  TrackerValidationRuleInterface,
} from '@objectiv/tracker-core';
import { TrackerConsole } from './TrackerConsole';
import { makeLocationContextValidationRule } from './validationRules/makeLocationContextValidationRule';
import { makeMissingGlobalContextValidationRule } from './validationRules/makeMissingGlobalContextValidationRule';
import { makeUniqueGlobalContextValidationRule } from './validationRules/makeUniqueGlobalContextValidationRule';

/**
 * Validates a number of rules related to the Open Taxonomy:
 * - ApplicationContext must be present once in Global Contexts.
 * - RootLocationContext must be present once, in position 0, of the Location Stack.
 */
export const OpenTaxonomyValidationPlugin = new (class implements TrackerPluginInterface {
  readonly pluginName = `OpenTaxonomyValidationPlugin`;
  validationRules: TrackerValidationRuleInterface[] = [];
  initialized = false;

  /**
   * At initialization, we retrieve TrackerPlatform and initialize all Validation Rules.
   */
  initialize({ platform }: TrackerInterface) {
    this.validationRules = [
      makeUniqueGlobalContextValidationRule({
        platform,
        logPrefix: this.pluginName,
      }),
      makeMissingGlobalContextValidationRule({
        platform,
        logPrefix: this.pluginName,
        contextName: GlobalContextName.ApplicationContext,
      }),
      makeMissingGlobalContextValidationRule({
        platform,
        logPrefix: this.pluginName,
        contextName: GlobalContextName.PathContext,
        eventMatches: (event: EventToValidate) => event.__interactive_event === true,
      }),
      makeLocationContextValidationRule({
        platform,
        logPrefix: this.pluginName,
        contextName: LocationContextName.RootLocationContext,
        once: true,
        position: 0,
        eventMatches: (event: EventToValidate) => event.__interactive_event === true,
      }),
    ];

    TrackerConsole.log(`%c｢objectiv:${this.pluginName}｣ Initialized`, 'font-weight: bold');

    this.initialized = true;
  }

  /**
   * Performs Open Taxonomy related validation checks
   */
  validate(event: TrackerEvent): void {
    if (!this.initialized) {
      TrackerConsole.error(`｢objectiv:${this.pluginName}｣ Cannot validate. Make sure to initialize the plugin first.`);
      return;
    }

    this.validationRules.forEach((validationRule) => validationRule.validate(event));
  }

  /**
   * Make this plugin always active.
   */
  isUsable(): boolean {
    return true;
  }
})();
