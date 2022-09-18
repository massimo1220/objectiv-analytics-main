/*
 * Copyright 2021-2022 Objectiv B.V.
 */

/**
 * Helper function to get the current Location href
 */
export const getLocationHref = () => {
  if (typeof location === 'undefined') {
    return undefined;
  }

  return location.href;
};
