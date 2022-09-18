/*
 * Copyright 2021-2022 Objectiv B.V.
 */

/**
 * Kudos to the original poster for this: https://github.com/facebook/jest/issues/5785#issuecomment-769475904
 *
 * Helps prevent error logs blowing up as a result of expecting an error to be thrown,
 * when using a library (such as enzyme)
] */
export const expectToThrow = (func: () => unknown, error?: JestToErrorArg): void => {
  const spy = jest.spyOn(console, 'error');
  spy.mockImplementation(() => {});

  expect(func).toThrow(error);

  spy.mockRestore();
};

type JestToErrorArg = Parameters<jest.Matchers<unknown, () => unknown>['toThrow']>[0];
