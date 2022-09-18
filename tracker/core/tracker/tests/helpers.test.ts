/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { isBrowser, isDevMode, makeId, waitForPromise } from '../src';

describe('helpers', () => {
  describe('waitForPromise', () => {
    it('resolves - immediate', () => {
      return expect(
        waitForPromise({
          predicate: () => true,
          intervalMs: 1,
          timeoutMs: 1,
        })
      ).resolves.toBe(true);
    });

    it('resolves - async', () => {
      return expect(
        waitForPromise({
          predicate: jest.fn().mockReturnValueOnce(false).mockReturnValueOnce(true),
          intervalMs: 1,
          timeoutMs: 1,
        })
      ).resolves.toBe(true);
    });

    it('rejects - timeout', () => {
      return expect(
        waitForPromise({
          predicate: () => false,
          intervalMs: 1,
          timeoutMs: 1,
        })
      ).resolves.toBe(false);
    });
  });

  describe('makeId', () => {
    const testCases: [input: unknown, normalize: boolean | undefined, output: string | null][] = [
      [undefined, true, null],
      [null, true, null],
      [false, true, null],
      [true, true, null],
      [[], true, null],
      [{}, true, null],

      [0, true, '0'],
      ['', true, null],
      ['_', true, null],
      ['-', true, null],
      ['-_', true, null],
      ['-_a', true, 'a'],
      ['a_-', true, 'a'],
      ['a-_a', true, 'a-_a'],
      ['AbCdE', true, 'abcde'],
      ['Click Me!', true, 'click-me'],
      ['X', true, 'x'],
      ['What - How', true, 'what-how'],
      ['Quite a "LONG" sentence! (annoying uh?)', true, 'quite-a-long-sentence-annoying-uh'],
      ['Quite a "LONG" sentence! (annoying uh?)', false, 'Quite a "LONG" sentence! (annoying uh?)'],
      [12345, false, '12345'],
      [12345, undefined, '12345'],
    ];

    testCases.forEach(([input, normalize, output]) =>
      it(`${JSON.stringify(input)} (normalize: ${normalize ? 'yes' : 'no'}) -> ${JSON.stringify(output)}`, () => {
        expect(makeId(input, normalize)).toBe(output);
      })
    );
  });

  describe('isDevMode', () => {
    const OLD_ENV = process.env;

    beforeEach(() => {
      process.env = { ...OLD_ENV };
    });

    afterAll(() => {
      process.env = OLD_ENV;
    });

    it(`should return false (production)`, () => {
      process.env.NODE_ENV = 'production';
      expect(isDevMode()).toBe(false);
    });

    it(`should return false (NODE_ENV not set)`, () => {
      Object.defineProperty(process, 'env', { value: {}, configurable: true });
      expect(isDevMode()).toBe(false);
    });

    it(`should return true (development)`, () => {
      process.env.NODE_ENV = 'development';
      expect(isDevMode()).toBe(true);
    });

    it(`should return true (test)`, () => {
      process.env.NODE_ENV = 'test';
      expect(isDevMode()).toBe(true);
    });
  });

  describe('isBrowser', () => {
    it(`should return false`, () => {
      expect(isBrowser()).toBe(false);
    });
  });
});
