/*
 * Copyright 2022 Objectiv B.V.
 * @jest-environment node
 */
import { MockConsoleImplementation } from '@objectiv/testing-tools';
import { generateGUID, TrackerEvent } from '@objectiv/tracker-core';
import { LocaleContextPlugin } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('LocaleContextPlugin - node', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  describe('Without developer tools', () => {
    let objectivGlobal = globalThis.objectiv;

    beforeEach(() => {
      jest.clearAllMocks();
      globalThis.objectiv.devTools = undefined;
    });

    afterEach(() => {
      globalThis.objectiv = objectivGlobal;
    });

    it('should not log', () => {
      new LocaleContextPlugin({
        idFactoryFunction: () => location.pathname.split('/')[1] ?? null,
      });
      expect(MockConsoleImplementation.log).not.toHaveBeenCalled();
    });

    it('should not console error when no factory function has been provided', async () => {
      //@ts-ignore
      new LocaleContextPlugin({});

      expect(MockConsoleImplementation.error).not.toHaveBeenCalled();
    });

    it('should not log failure to enrich', async () => {
      const testLocaleContextPlugin = new LocaleContextPlugin({
        idFactoryFunction: () => null,
      });
      testLocaleContextPlugin.isUsable = () => true;
      testLocaleContextPlugin.enrich(new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() }));
      expect(MockConsoleImplementation.warn).not.toHaveBeenCalled();
    });

    it('enrich should not console error if the plugin was not initialized correctly', async () => {
      const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() });
      //@ts-ignore
      new LocaleContextPlugin().enrich(testEvent);

      expect(MockConsoleImplementation.warn).not.toHaveBeenCalled();
    });

    it('enrich should not console error if the given languageFactoryFunction returns an invalid code', async () => {
      const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() });
      new LocaleContextPlugin({ languageFactoryFunction: () => 'nope' }).enrich(testEvent);

      expect(MockConsoleImplementation.warn).not.toHaveBeenCalled();
    });

    it('enrich should not console error if the given countryFactoryFunction returns an invalid code', async () => {
      const testEvent = new TrackerEvent({ _type: 'test-event', id: generateGUID(), time: Date.now() });
      new LocaleContextPlugin({ countryFactoryFunction: () => 'nope' }).enrich(testEvent);

      expect(MockConsoleImplementation.warn).not.toHaveBeenCalled();
    });
  });
});
