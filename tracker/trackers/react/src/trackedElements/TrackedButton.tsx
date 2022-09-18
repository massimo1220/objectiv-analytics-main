/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import React, { ComponentProps, forwardRef, Ref } from 'react';
import { TrackedPressableContext } from '../trackedContexts/TrackedPressableContext';
import { TrackedElementProps } from '../types';

/**
 * Generates a TrackedPressableContext preconfigured with a <button> Element as Component.
 */
export const TrackedButton = forwardRef(
  ({ objectiv, ...nativeProps }: TrackedElementProps<ComponentProps<'button'>>, ref: Ref<HTMLButtonElement>) => (
    <TrackedPressableContext objectiv={{ ...objectiv, Component: 'button' }} {...nativeProps} ref={ref} />
  )
);
