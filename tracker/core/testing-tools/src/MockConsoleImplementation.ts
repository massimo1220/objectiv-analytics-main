/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TrackerConsoleImplementation } from '@objectiv/tracker-core';

export const MockConsoleImplementation: TrackerConsoleImplementation = {
  debug: jest.fn(),
  error: jest.fn(),
  group: jest.fn(),
  groupCollapsed: jest.fn(),
  groupEnd: jest.fn(),
  info: jest.fn(),
  log: jest.fn(),
  warn: jest.fn(),
};
