/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import React, { forwardRef, Ref } from 'react';
import { TrackedInputContext } from '../trackedContexts/TrackedInputContext';
import { TrackedInputProps } from '../types';

/**
 * Generates a TrackedInputContext preconfigured with a <input type="radio"> Element as Component.
 */
export const TrackedInputRadio = forwardRef(
  ({ objectiv, ...nativeProps }: TrackedInputProps, ref: Ref<HTMLInputElement>) => {
    if (globalThis.objectiv.devTools && nativeProps.type && nativeProps.type !== 'radio') {
      globalThis.objectiv.devTools.TrackerConsole.warn(
        `｢objectiv｣ TrackedInputRadio type attribute can only be set to 'radio'.`
      );
    }

    return (
      <TrackedInputContext
        objectiv={{
          ...objectiv,
          Component: 'input',
        }}
        type={'radio'}
        {...nativeProps}
        ref={ref}
      />
    );
  }
);
