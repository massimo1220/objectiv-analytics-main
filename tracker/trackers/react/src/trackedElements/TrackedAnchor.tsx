/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import React, { ComponentProps, forwardRef, Ref } from 'react';
import { TrackedLinkContext } from '../trackedContexts/TrackedLinkContext';
import { TrackedElementProps } from '../types';

/**
 * Generates a TrackedAnchorContext preconfigured with an <a> Element as Component.
 */
export const TrackedAnchor = forwardRef(
  ({ objectiv, ...nativeProps }: TrackedElementProps<ComponentProps<'a'>>, ref: Ref<HTMLAnchorElement>) => (
    <TrackedLinkContext objectiv={{ ...objectiv, Component: 'a' }} {...nativeProps} ref={ref} />
  )
);
