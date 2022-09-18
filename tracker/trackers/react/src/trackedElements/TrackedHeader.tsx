/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import React, { ComponentProps, forwardRef, Ref } from 'react';
import { TrackedContentContext } from '../trackedContexts/TrackedContentContext';
import { TrackedElementWithOptionalIdProps } from '../types';

/**
 * Generates a TrackedContentContext preconfigured with a <header> Element as Component.
 */
export const TrackedHeader = forwardRef(
  (
    { objectiv, ...nativeProps }: TrackedElementWithOptionalIdProps<ComponentProps<'header'>>,
    ref: Ref<HTMLElement>
  ) => (
    <TrackedContentContext
      objectiv={{ ...objectiv, Component: 'header', id: objectiv?.id ?? nativeProps.id ?? 'header' }}
      {...nativeProps}
      ref={ref}
    />
  )
);
