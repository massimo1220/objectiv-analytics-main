/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import React, { ComponentProps, forwardRef, Ref } from 'react';
import { TrackedContentContext } from '../trackedContexts/TrackedContentContext';
import { TrackedElementWithOptionalIdProps } from '../types';

/**
 * Generates a TrackedContentContext preconfigured with a <main> Element as Component.
 */
export const TrackedMain = forwardRef(
  ({ objectiv, ...nativeProps }: TrackedElementWithOptionalIdProps<ComponentProps<'main'>>, ref: Ref<HTMLElement>) => (
    <TrackedContentContext objectiv={{ ...objectiv, Component: 'main' }} {...nativeProps} ref={ref} />
  )
);
