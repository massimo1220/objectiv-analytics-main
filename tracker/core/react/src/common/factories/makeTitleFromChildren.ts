/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { ReactNode } from 'react';
import { recursiveGetTextFromChildren } from './recursiveGetTextFromChildren';

/**
 * Retrieve text from given ReactNode children.
 * The resulting text may be used, among others, to infer a valid text and identifier for a Button.
 */
export const makeTitleFromChildren = (children: ReactNode): string => {
  return recursiveGetTextFromChildren(children)?.trim() ?? '';
};
