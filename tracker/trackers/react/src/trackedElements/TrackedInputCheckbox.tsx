/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import React, { forwardRef, Ref } from 'react';
import { TrackedInputContext } from '../trackedContexts/TrackedInputContext';
import { TrackedInputProps } from '../types';

/**
 * Generates a TrackedInputContext preconfigured with a <input type="checkbox"> Element as Component.
 */
export const TrackedInputCheckbox = forwardRef(
  ({ objectiv, ...nativeProps }: TrackedInputProps, ref: Ref<HTMLInputElement>) => {
    if (globalThis.objectiv.devTools && nativeProps.type && nativeProps.type !== 'checkbox') {
      globalThis.objectiv.devTools.TrackerConsole.warn(
        `｢objectiv｣ TrackedInputCheckbox type attribute can only be set to 'checkbox'.`
      );
    }

    return (
      <TrackedInputContext
        objectiv={{
          ...objectiv,
          Component: 'input',
        }}
        type={'checkbox'}
        {...nativeProps}
        ref={ref}
      />
    );
  }
);
