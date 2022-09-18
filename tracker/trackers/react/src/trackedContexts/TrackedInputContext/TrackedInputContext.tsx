/*
 * Copyright 2022 Objectiv B.V.
 */

import React, { ComponentProps, PropsWithRef, Ref } from 'react';
import { ObjectivComponentProp, ObjectivIdProps, ObjectivValueTrackingProps } from '../../types';
import { TrackedInputContextCheckbox } from './TrackedInputContextCheckbox';
import { TrackedInputContextRadio } from './TrackedInputContextRadio';
import { TrackedInputContextSelectMultiple } from './TrackedInputContextSelectMultiple';
import { TrackedInputContextSelectSingle } from './TrackedInputContextSelectSingle';
import { TrackedValueBasedInputContext } from './TrackedValueBasedInputContext';

/**
 * TrackedInputContext has a few additional properties to configure it.
 */
export type TrackedInputContextObjectivProp = ObjectivComponentProp & ObjectivIdProps & ObjectivValueTrackingProps;
export type TrackedInputContextProps<O = TrackedInputContextObjectivProp> = (
  | ComponentProps<'input'>
  | ComponentProps<'select'>
) & {
  /**
   * Type prop needs to be redefined here, because it doesn't overlap between input and select
   */
  type?: unknown;

  /**
   * The Objectiv configuration object
   */
  objectiv: O;
};

/**
 * Generates a new React Element already wrapped in an InputContext.
 *
 * This Component is a factory to pick the correct TrackedInputContext implementation based on the given props.
 *
 * If no custom implementation is found for the given Component/type combination, the TrackedValueBasedInputContext
 * is used.
 */
export const TrackedInputContext = React.forwardRef(
  (props: TrackedInputContextProps, ref: Ref<HTMLInputElement | HTMLSelectElement>) => {
    if (props.objectiv.Component === 'select' && !props.multiple) {
      return <TrackedInputContextSelectSingle {...props} ref={ref} />;
    }

    if (props.objectiv.Component === 'select' && props.multiple) {
      return <TrackedInputContextSelectMultiple {...props} ref={ref} />;
    }

    if (props.objectiv.Component === 'input' && props.type === 'radio') {
      return <TrackedInputContextRadio {...props} ref={ref} />;
    }

    if (props.objectiv.Component === 'input' && props.type === 'checkbox') {
      return <TrackedInputContextCheckbox {...props} ref={ref} />;
    }

    return <TrackedValueBasedInputContext {...props} ref={ref} />;
  }
) as (props: PropsWithRef<TrackedInputContextProps>) => JSX.Element;
