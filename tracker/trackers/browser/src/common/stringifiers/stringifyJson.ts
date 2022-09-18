/*
 * Copyright 2021-2022 Objectiv B.V.
 */

/**
 * JSON Objects stringifier
 */
export const stringifyJson = (object: unknown): string => {
  return JSON.stringify(object);
};
