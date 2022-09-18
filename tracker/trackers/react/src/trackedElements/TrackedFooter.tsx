/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import React, { ComponentProps, forwardRef, Ref } from 'react';
import { TrackedContentContext } from '../trackedContexts/TrackedContentContext';
import { TrackedElementWithOptionalIdProps } from '../types';

/**
 * Generates a TrackedContentContext preconfigured with a <footer> Element as Component.
 */
export const TrackedFooter = forwardRef(
  (
    { objectiv, ...nativeProps }: TrackedElementWithOptionalIdProps<ComponentProps<'footer'>>,
    ref: Ref<HTMLElement>
  ) => (
    <TrackedContentContext
      objectiv={{ ...objectiv, Component: 'footer', id: objectiv?.id ?? nativeProps.id ?? 'footer' }}
      {...nativeProps}
      ref={ref}
    />
  )
);
