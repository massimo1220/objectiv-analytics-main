/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import React, { ComponentProps, forwardRef, Ref } from 'react';
import { TrackedContentContext } from '../trackedContexts/TrackedContentContext';
import { TrackedElementProps } from '../types';

/**
 * Generates a TrackedContentContext preconfigured with a <section> Element as Component.
 */
export const TrackedSection = forwardRef(
  ({ objectiv, ...nativeProps }: TrackedElementProps<ComponentProps<'section'>>, ref: Ref<HTMLElement>) => (
    <TrackedContentContext objectiv={{ ...objectiv, Component: 'section' }} {...nativeProps} ref={ref} />
  )
);
