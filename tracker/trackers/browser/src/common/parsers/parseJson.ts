/*
 * Copyright 2021-2022 Objectiv B.V.
 */

/**
 * JSON Objects parser
 */
export const parseJson = (stringifiedObject: string | null) => {
  if (stringifiedObject === null) {
    return null;
  }

  return JSON.parse(stringifiedObject);
};
