/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeRootLocationContext } from '@objectiv/tracker-core';
import React from 'react';
import { ContentContextWrapperProps } from './ContentContextWrapper';
import { LocationContextWrapper } from './LocationContextWrapper';

/**
 * Wraps its children in an RootLocationContext.
 */
export const RootLocationContextWrapper = ({ children, id }: ContentContextWrapperProps) => (
  <LocationContextWrapper locationContext={makeRootLocationContext({ id })}>
    {(trackingContext) => (typeof children === 'function' ? children(trackingContext) : children)}
  </LocationContextWrapper>
);
