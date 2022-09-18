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
 * TrackedInputContext implementation for selects.
 */
export type TrackedInputContextSelectSingleProps = ComponentProps<'select'> & {
  objectiv: ObjectivComponentProp & ObjectivIdProps & ObjectivValueTrackingProps;
};

/**
 * Event definition for TrackedInputContextSelectSingle
 */
export type TrackedInputContextSelectSingleEvent =
  | FocusEvent<HTMLSelectElement>
  | ChangeEvent<HTMLSelectElement>
  | React.MouseEvent<HTMLSelectElement>;

/**
 * TrackedInputContextSelectSingle implementation
 */
export const TrackedInputContextSelectSingle = forwardRef(
  (props: TrackedInputContextSelectSingleProps, ref: Ref<HTMLSelectElement>) => {
    const {
      objectiv: { Component, id, normalizeId = true, trackValue = false, stateless = false, eventHandler = 'onChange' },
      ...nativeProps
    } = props;

    const initialValue = nativeProps.value ?? nativeProps.defaultValue;
    const [previousValue, setPreviousValue] = useState<string>(normalizeValue(initialValue));
    const locationStack = useLocationStack();

    let selectId: string | null | undefined = id ?? nativeProps.id;
    if (selectId && normalizeId) {
      selectId = makeId(selectId);
    }

    const handleEvent = async (event: TrackedInputContextSelectSingleEvent, trackingContext: TrackingContext) => {
      const eventTarget = event.target as HTMLSelectElement;
      const valueToMonitor = normalizeValue(eventTarget.value);

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
        if (selectId && trackValue) {
          eventTrackerParameters.globalContexts.push(
            makeInputValueContext({
              id: selectId,
              value: normalizeValue(eventTarget.value),
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

    if (!selectId) {
      if (globalThis.objectiv.devTools) {
        const locationPath = globalThis.objectiv.devTools.getLocationPath(locationStack);
        globalThis.objectiv.devTools.TrackerConsole.error(
          `｢objectiv｣ Could not generate a valid id for InputContext:select @ ${locationPath}. Please provide the \`objectiv.id\` property.`
        );
      }
      return <Component {...componentProps} />;
    }

    return (
      <InputContextWrapper id={selectId}>
        {(trackingContext) => (
          <Component
            {...componentProps}
            {...{
              [eventHandler]: (event: TrackedInputContextSelectSingleEvent) => handleEvent(event, trackingContext),
            }}
          />
        )}
      </InputContextWrapper>
    );
  }
) as <T>(props: PropsWithRef<TrackedContextProps<T>>) => JSX.Element;
