/*
 * Copyright 2022 Objectiv B.V.
 */

import { GlobalContexts, LocationStack, makeId, makeInputValueContext } from '@objectiv/tracker-core';
import {
  EventTrackerParameters,
  InputContextWrapper,
  TrackingContext,
  trackInputChangeEvent,
  useLocationStack,
} from '@objectiv/tracker-react-core';
import React, { ChangeEvent, ComponentProps, FocusEvent, forwardRef, PropsWithRef, Ref, useState } from 'react';
import { ObjectivComponentProp, ObjectivIdProps, TrackedContextProps, ObjectivValueTrackingProps } from '../../types';
import { isBlurEvent, isChangeEvent, isClickEvent, normalizeValue } from './TrackedInputContextShared';

/**
 * TrackedInputContext implementation for checkboxes.
 * Monitors the `checked` attribute and automatically tracks `InputChangeEvent` when the given Component receives an
 * `onChange` and `checked` changed.
 * Optionally tracks the input's `checked` attribute as InputValueContext.
 */
export type TrackedInputContextCheckboxProps = ComponentProps<'input'> & {
  objectiv: ObjectivComponentProp & ObjectivIdProps & ObjectivValueTrackingProps;
};

/**
 * Event definition for TrackedInputContextCheckbox
 */
export type TrackedInputContextCheckboxEvent =
  | FocusEvent<HTMLInputElement>
  | ChangeEvent<HTMLInputElement>
  | React.MouseEvent<HTMLInputElement>;

/**
 * TrackedInputContextCheckbox implementation
 */
export const TrackedInputContextCheckbox = forwardRef(
  (props: TrackedInputContextCheckboxProps, ref: Ref<HTMLInputElement>) => {
    const {
      objectiv: { Component, id, normalizeId = true, trackValue = false, stateless = false, eventHandler = 'onChange' },
      ...nativeProps
    } = props;

    const initialValue = nativeProps.checked ?? nativeProps.defaultChecked;
    const [previousValue, setPreviousValue] = useState<string>(normalizeValue(initialValue));
    const locationStack = useLocationStack();

    // Use the given `id` or the native `id` or attempt to automatically generate one with either `name` or `value`
    const nameAttribute: string | null = nativeProps.name ? nativeProps.name : null;
    const valueAttribute: string | null = nativeProps.value ? nativeProps.value.toString() : null;
    let inputId: string | null = id ?? nativeProps.id ?? nameAttribute ?? valueAttribute;
    if (inputId && normalizeId) {
      inputId = makeId(inputId);
    }

    const handleEvent = async (event: TrackedInputContextCheckboxEvent, trackingContext: TrackingContext) => {
      const eventTarget = event.target as HTMLInputElement;
      const valueToMonitor = normalizeValue(eventTarget.checked);

      if (stateless || previousValue !== valueToMonitor) {
        setPreviousValue(valueToMonitor);

        const eventTrackerParameters: EventTrackerParameters & {
          globalContexts: GlobalContexts;
          locationStack: LocationStack;
        } = {
          ...trackingContext,
          globalContexts: [],
        };

        // Add InputValueContext if trackValue has been set
        if (inputId && trackValue) {
          eventTrackerParameters.globalContexts.push(
            makeInputValueContext({
              id: inputId,
              value: normalizeValue(eventTarget.checked),
            })
          );
        }

        trackInputChangeEvent(eventTrackerParameters);
      }

      if (isBlurEvent(event)) {
        nativeProps.onBlur && nativeProps.onBlur(event);
      }

      if (isChangeEvent(event)) {
        nativeProps.onChange && nativeProps.onChange(event);
      }

      if (isClickEvent(event)) {
        nativeProps.onClick && nativeProps.onClick(event);
      }
    };

    const componentProps = {
      ...nativeProps,
      ...(ref ? { ref } : {}),
    };

    if (!inputId) {
      if (globalThis.objectiv.devTools) {
        const locationPath = globalThis.objectiv.devTools.getLocationPath(locationStack);
        globalThis.objectiv.devTools.TrackerConsole.error(
          `｢objectiv｣ Could not generate a valid id for InputContext:checkbox @ ${locationPath}. Please provide the \`objectiv.id\` property.`
        );
      }

      return <Component {...componentProps} />;
    }

    return (
      <InputContextWrapper id={inputId}>
        {(trackingContext) => (
          <Component
            {...componentProps}
            {...{
              [eventHandler]: (event: TrackedInputContextCheckboxEvent) => handleEvent(event, trackingContext),
            }}
          />
        )}
      </InputContextWrapper>
    );
  }
) as <T>(props: PropsWithRef<TrackedContextProps<T>>) => JSX.Element;
