/*
 * Copyright 2022 Objectiv B.V.
 */

import { ContextsConfig, makeLocaleContext, TrackerPluginInterface } from '@objectiv/tracker-core';
import { CountryCodes } from './generated/CountryCodes';
import { LanguageCodes } from './generated/LanguageCodes';

/**
 * Factory functions may return string, null or undefined
 */
export type LocaleContextPluginFactoryFunction = () => string | null | undefined;

/**
 * The configuration object of LocaleContextPlugin. Developers must specify at least one of the factory functions.
 */
export type LocaleContextPluginConfig =
  | {
      idFactoryFunction: LocaleContextPluginFactoryFunction;
      languageFactoryFunction?: LocaleContextPluginFactoryFunction;
      countryFactoryFunction?: LocaleContextPluginFactoryFunction;
    }
  | {
      idFactoryFunction?: LocaleContextPluginFactoryFunction;
      languageFactoryFunction: LocaleContextPluginFactoryFunction;
      countryFactoryFunction?: LocaleContextPluginFactoryFunction;
    }
  | {
      idFactoryFunction?: LocaleContextPluginFactoryFunction;
      languageFactoryFunction?: LocaleContextPluginFactoryFunction;
      countryFactoryFunction: LocaleContextPluginFactoryFunction;
    };

/**
 * The LocaleContext Plugin executes the given idFactoryFunction to retrieve the identifier to factor a
 * LocaleContext which is attached to the Event's Global Contexts.
 * It implements the `enrich` lifecycle method. This ensures the locale is determined before each Event is sent.
 */
export class LocaleContextPlugin implements TrackerPluginInterface {
  readonly pluginName = `LocaleContextPlugin`;
  readonly initialized: boolean = false;
  readonly idFactoryFunction: LocaleContextPluginFactoryFunction = () => null;
  readonly languageFactoryFunction: LocaleContextPluginFactoryFunction = () => null;
  readonly countryFactoryFunction: LocaleContextPluginFactoryFunction = () => null;

  /**
   * The constructor is merely responsible for processing the given LocaleContextPluginConfig.
   */
  constructor(config: LocaleContextPluginConfig) {
    if (!config?.idFactoryFunction && !config?.countryFactoryFunction && !config?.languageFactoryFunction) {
      globalThis.objectiv.devTools?.TrackerConsole.error(
        `%c｢objectiv:${this.pluginName}｣ Please specify at least one factory function.`,
        'font-weight: bold'
      );
      return;
    }

    this.idFactoryFunction = config.idFactoryFunction ?? this.idFactoryFunction;
    this.languageFactoryFunction = config.languageFactoryFunction ?? this.languageFactoryFunction;
    this.countryFactoryFunction = config.countryFactoryFunction ?? this.countryFactoryFunction;
    this.initialized = true;

    globalThis.objectiv.devTools?.TrackerConsole.log(
      `%c｢objectiv:${this.pluginName}｣ Initialized`,
      'font-weight: bold'
    );
  }

  /**
   * Generate a fresh LocaleContext before each TrackerEvent is handed over to the TrackerTransport.
   *
   */
  enrich(contexts: Required<ContextsConfig>): void {
    if (!this.initialized) {
      globalThis.objectiv.devTools?.TrackerConsole.warn(
        `%c｢objectiv:${this.pluginName}｣ Skipped enrich. Please initialize with at least one factory faction.`,
        'font-weight: bold'
      );
      return;
    }

    // Generate and validate language code.
    const maybeLanguageCode = this.languageFactoryFunction();
    const languageCode = maybeLanguageCode && LanguageCodes.includes(maybeLanguageCode) ? maybeLanguageCode : null;
    if (maybeLanguageCode && !languageCode) {
      globalThis.objectiv.devTools?.TrackerConsole.warn(
        `%c｢objectiv:${this.pluginName}｣ Language code is not ISO 639-1. Got: ${maybeLanguageCode}.`,
        'font-weight: bold'
      );
      return;
    }

    // Generate and validate country code.
    const maybeCountryCode = this.countryFactoryFunction();
    const countryCode = maybeCountryCode && CountryCodes.includes(maybeCountryCode) ? maybeCountryCode : null;
    if (maybeCountryCode && !countryCode) {
      globalThis.objectiv.devTools?.TrackerConsole.warn(
        `%c｢objectiv:${this.pluginName}｣ Country code is not ISO 3166-1 alpha-2. Got: ${maybeCountryCode}.`,
        'font-weight: bold'
      );
      return;
    }

    // Generate LocaleContext id. We use either what the developer specified, or make one with language and country.
    let localeContextId = this.idFactoryFunction();
    if (!localeContextId) {
      if (languageCode && countryCode) {
        localeContextId = `${languageCode}_${countryCode}`;
      } else {
        localeContextId = `${languageCode ?? ''}${countryCode ?? ''}`;
      }
    }

    if (!localeContextId) {
      globalThis.objectiv.devTools?.TrackerConsole.warn(
        `%c｢objectiv:${this.pluginName}｣ Cannot enrich. Could not generate a valid LocaleContext.`,
        'font-weight: bold'
      );
      return;
    }

    const localeContext = makeLocaleContext({
      id: localeContextId,
      language_code: languageCode,
      country_code: countryCode,
    });
    contexts.global_contexts.push(localeContext);
  }

  /**
   * Make this plugin always usable. The provided idFactoryFunction may return `null` when detection is impossible.
   */
  isUsable(): boolean {
    return true;
  }
}
