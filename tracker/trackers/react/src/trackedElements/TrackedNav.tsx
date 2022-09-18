/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import React, { ComponentProps, forwardRef, Ref } from 'react';
import { TrackedNavigationContext } from '../trackedContexts/TrackedNavigationContext';
import { TrackedElementWithOptionalIdProps } from '../types';

/**
 * Generates a TrackedNavigationContext preconfigured with a <nav> Element as Component.
 */
export const TrackedNav = forwardRef(
  ({ objectiv, ...nativeProps }: TrackedElementWithOptionalIdProps<ComponentProps<'nav'>>, ref: Ref<HTMLElement>) => (
    <TrackedNavigationContext objectiv={{ ...objectiv, Component: 'nav' }} {...nativeProps} ref={ref} />
  )
);
