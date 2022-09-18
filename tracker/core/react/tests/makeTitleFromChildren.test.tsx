/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import React from 'react';
import { ReactNode } from 'react';
import { makeTitleFromChildren } from '../src';

describe('makeTitleFromChildren', () => {
  const testCases: [input: ReactNode, output: string][] = [
    [undefined, ''],
    [null, ''],
    [false, ''],
    [true, ''],
    [[], ''],
    [{}, ''],
    ['', ''],
    [0, '0'],
    [123, '123'],
    [456.12, '456.12'],
    [['test', 456.12, 'abc'], 'test 456.12 abc'],
    [<div>what?</div>, 'what?'],
    [
      <div>
        <span>yes!</span>
      </div>,
      'yes!',
    ],
    [
      <div>
        <img alt={'orly?'} />
        <span>NOPE</span>
      </div>,
      'NOPE',
    ],
  ];

  testCases.forEach(([input, output]) =>
    it(`${JSON.stringify(input)} -> ${JSON.stringify(output)}`, () => {
      expect(makeTitleFromChildren(input)).toBe(output);
    })
  );
});
