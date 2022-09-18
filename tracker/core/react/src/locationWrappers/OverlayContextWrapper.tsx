/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeOverlayContext } from '@objectiv/tracker-core';
import React from 'react';
import { ContentContextWrapperProps } from './ContentContextWrapper';
import { LocationContextWrapper } from './LocationContextWrapper';

/**
 * Wraps its children in an OverlayContext.
 */
export const OverlayContextWrapper = ({ children, id }: ContentContextWrapperProps) => (
  <LocationContextWrapper locationContext={makeOverlayContext({ id })}>
    {(trackingContext) => (typeof children === 'function' ? children(trackingContext) : children)}
  </LocationContextWrapper>
);
