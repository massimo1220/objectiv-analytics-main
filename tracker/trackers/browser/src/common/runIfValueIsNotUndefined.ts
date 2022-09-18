/*
 * Copyright 2021-2022 Objectiv B.V.
 */

/**
 * Executes `functionToRun(value)` only if the given `value` is not `undefined`
 */
export const runIfValueIsNotUndefined = (functionToRun: Function, value: unknown) => {
  if (typeof value === 'undefined') {
    return undefined;
  }

  return functionToRun(value);
};
