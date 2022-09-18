/*
 * Copyright 2022 Objectiv B.V.
 */

import { matchUUID, MockConsoleImplementation } from '@objectiv/testing-tools';
import { generateGUID, GlobalContextName, Tracker, TrackerEvent } from '@objectiv/tracker-core';
import { LocaleContextPlugin } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('LocaleContextPlugin', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  it('should console error when no factory function has been provided', async () => {
    //@ts-ignore
    new LocaleContextPlugin({});

    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '%c｢objectiv:LocaleContextPlugin｣ Please specify at least one factory function.',
      'font-weight: bold'
    );
  });

  it('enrich should console error if the plugin was not initialized correctly', async () => {
    const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() });
    //@ts-ignore
    new LocaleContextPlugin().enrich(testEvent);

    expect(MockConsoleImplementation.warn).toHaveBeenCalledWith(
      '%c｢objectiv:LocaleContextPlugin｣ Skipped enrich. Please initialize with at least one factory faction.',
      'font-weight: bold'
    );
  });

  it('enrich should console error if the given factory does not return a value - idFactoryFunction', async () => {
    const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() });
    new LocaleContextPlugin({ idFactoryFunction: () => null }).enrich(testEvent);

    expect(MockConsoleImplementation.warn).toHaveBeenCalledWith(
      '%c｢objectiv:LocaleContextPlugin｣ Cannot enrich. Could not generate a valid LocaleContext.',
      'font-weight: bold'
    );
  });

  it('enrich should console error if the given factory does not return a value - languageFactoryFunction', async () => {
    const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() });
    new LocaleContextPlugin({ languageFactoryFunction: () => null }).enrich(testEvent);

    expect(MockConsoleImplementation.warn).toHaveBeenCalledWith(
      '%c｢objectiv:LocaleContextPlugin｣ Cannot enrich. Could not generate a valid LocaleContext.',
      'font-weight: bold'
    );
  });

  it('enrich should console error if the given languageFactoryFunction returns an invalid code', async () => {
    const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() });
    new LocaleContextPlugin({ languageFactoryFunction: () => 'nope' }).enrich(testEvent);

    expect(MockConsoleImplementation.warn).toHaveBeenCalledWith(
      '%c｢objectiv:LocaleContextPlugin｣ Language code is not ISO 639-1. Got: nope.',
      'font-weight: bold'
    );
  });

  it('enrich should console error if the given countryFactoryFunction returns an invalid code', async () => {
    const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() });
    new LocaleContextPlugin({ countryFactoryFunction: () => 'nope' }).enrich(testEvent);

    expect(MockConsoleImplementation.warn).toHaveBeenCalledWith(
      '%c｢objectiv:LocaleContextPlugin｣ Country code is not ISO 3166-1 alpha-2. Got: nope.',
      'font-weight: bold'
    );
  });

  it('enrich should console error if the given factory does not return a value - countryFactoryFunction', async () => {
    const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() });
    new LocaleContextPlugin({ countryFactoryFunction: () => null }).enrich(testEvent);

    expect(MockConsoleImplementation.warn).toHaveBeenCalledWith(
      '%c｢objectiv:LocaleContextPlugin｣ Cannot enrich. Could not generate a valid LocaleContext.',
      'font-weight: bold'
    );
  });

  it('enrich should generate an identifier from language', async () => {
    const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() });
    new LocaleContextPlugin({ languageFactoryFunction: () => 'en' }).enrich(testEvent);
    expect(testEvent.global_contexts).toEqual([
      expect.objectContaining({
        _type: GlobalContextName.LocaleContext,
        id: 'en',
        language_code: 'en',
        country_code: null,
      }),
    ]);
  });

  it('enrich should generate an identifier from country', async () => {
    const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() });
    new LocaleContextPlugin({ countryFactoryFunction: () => 'US' }).enrich(testEvent);
    expect(testEvent.global_contexts).toEqual([
      expect.objectContaining({
        _type: GlobalContextName.LocaleContext,
        id: 'US',
        language_code: null,
        country_code: 'US',
      }),
    ]);
  });

  it('enrich should generate an identifier from language and country', async () => {
    const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() });
    new LocaleContextPlugin({ countryFactoryFunction: () => 'FR', languageFactoryFunction: () => 'en' }).enrich(
      testEvent
    );
    expect(testEvent.global_contexts).toEqual([
      expect.objectContaining({
        _type: GlobalContextName.LocaleContext,
        id: 'en_FR',
        language_code: 'en',
        country_code: 'FR',
      }),
    ]);
  });

  it('should not add the LocaleContext to the Event when `enrich` is executed by the Tracker', async () => {
    Object.defineProperty(window, 'location', {
      value: {
        pathname: '/',
      },
      writable: true,
    });

    const testTracker = new Tracker({
      applicationId: 'app-id',
      plugins: [
        new LocaleContextPlugin({
          idFactoryFunction: () => location.pathname.split('/')[1] ?? null,
        }),
      ],
    });

    const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() });
    const trackedEvent = await testTracker.trackEvent(testEvent);
    expect(trackedEvent.global_contexts).toHaveLength(0);
    expect(MockConsoleImplementation.warn).toHaveBeenCalledWith(
      '%c｢objectiv:LocaleContextPlugin｣ Cannot enrich. Could not generate a valid LocaleContext.',
      'font-weight: bold'
    );
  });

  it('should add the LocaleContext to the Event when `enrich` is executed by the Tracker', async () => {
    Object.defineProperty(window, 'location', {
      value: {
        pathname: '/en/home',
      },
      writable: true,
    });

    const testTracker = new Tracker({
      applicationId: 'app-id',
      plugins: [
        new LocaleContextPlugin({
          idFactoryFunction: () => location.pathname.split('/')[1] ?? null,
        }),
      ],
    });

    const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() });
    const trackedEvent = await testTracker.trackEvent(testEvent);
    expect(trackedEvent.global_contexts).toHaveLength(1);
    expect(trackedEvent.global_contexts).toEqual(
      expect.arrayContaining([
        {
          __instance_id: matchUUID,
          __global_context: true,
          _type: GlobalContextName.LocaleContext,
          id: 'en',
          country_code: null,
          language_code: null,
        },
      ])
    );
  });
});
