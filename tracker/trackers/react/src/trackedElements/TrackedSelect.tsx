/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import React, { forwardRef, Ref } from 'react';
import { TrackedInputContext } from '../trackedContexts/TrackedInputContext';
import { TrackedSelectProps } from '../types';

/**
 * Generates a TrackedInputContext preconfigured with a <select> Element as Component.
 */
export const TrackedSelect = forwardRef(
  ({ objectiv, ...nativeProps }: TrackedSelectProps, ref: Ref<HTMLSelectElement>) => (
    <TrackedInputContext objectiv={{ ...objectiv, Component: 'select' }} {...nativeProps} ref={ref} />
  )
);
