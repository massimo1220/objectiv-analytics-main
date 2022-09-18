/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import React, { ComponentProps, forwardRef, Ref } from 'react';
import { TrackedContentContext } from '../trackedContexts/TrackedContentContext';
import { TrackedElementProps } from '../types';

/**
 * Generates a TrackedContentContext preconfigured with a <div> Element as Component.
 */
export const TrackedDiv = forwardRef(
  ({ objectiv, ...nativeProps }: TrackedElementProps<ComponentProps<'div'>>, ref: Ref<HTMLDivElement>) => (
    <TrackedContentContext objectiv={{ ...objectiv, Component: 'div' }} {...nativeProps} ref={ref} />
  )
);
