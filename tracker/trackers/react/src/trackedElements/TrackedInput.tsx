/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import React, { forwardRef, Ref } from 'react';
import { TrackedInputContext } from '../trackedContexts/TrackedInputContext';
import { TrackedInputProps } from '../types';

/**
 * Generates a TrackedInputContext preconfigured with a <input> Element as Component.
 */
export const TrackedInput = forwardRef(
  ({ objectiv, ...nativeProps }: TrackedInputProps, ref: Ref<HTMLInputElement>) => {
    // Suggest to use TrackedInputCheckbox when type is 'checkbox'
    if (globalThis.objectiv.devTools) {
      if (nativeProps.type === 'checkbox') {
        globalThis.objectiv.devTools.TrackerConsole.warn(
          `｢objectiv｣ We recommend using TrackedInputCheckbox for tracking checkbox inputs.`
        );
      }
      if (nativeProps.type === 'radio') {
        globalThis.objectiv.devTools.TrackerConsole.warn(
          `｢objectiv｣ We recommend using TrackedInputRadio for tracking radio inputs.`
        );
      }
    }

    return <TrackedInputContext objectiv={{ ...objectiv, Component: 'input' }} {...nativeProps} ref={ref} />;
  }
);
