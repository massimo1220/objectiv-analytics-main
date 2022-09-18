/*
 * Copyright 2022 Objectiv B.V.
 */

import { CountryCodes, LanguageCodes } from '../src';

describe('Generated', () => {
  it('LanguageCodes should match snapshot', async () => {
    expect(LanguageCodes).toMatchSnapshot();
  });
  it('CountryCodes should match snapshot', async () => {
    expect(CountryCodes).toMatchSnapshot();
  });
});
