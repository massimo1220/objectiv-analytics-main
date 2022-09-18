/*
 * Copyright 2022 Objectiv B.V.
 */

import('../src');

describe('index', () => {
  it('Should have created the objectiv global', async () => {
    expect(globalThis.objectiv).not.toBeUndefined();
  });
});
