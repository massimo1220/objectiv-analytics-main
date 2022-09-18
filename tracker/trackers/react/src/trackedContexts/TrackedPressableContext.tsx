/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeId } from '@objectiv/tracker-core';
import {
  makeTitleFromChildren,
  PressableContextWrapper,
  trackPressEvent,
  useLocationStack,
} from '@objectiv/tracker-react-core';
import React, { forwardRef, PropsWithRef, Ref } from 'react';
import { TrackedPressableContextProps } from '../types';

/**
 * Generates a new React Element already wrapped in an PressableContext.
 * Automatically tracks PressEvent when the given Component receives an `onClick` SyntheticEvent.
 */
export const TrackedPressableContext = forwardRef(
  <T extends unknown>(props: TrackedPressableContextProps<T>, ref: Ref<unknown>) => {
    const {
      objectiv: { Component, id, normalizeId = true },
      ...nativeProps
    } = props;
    const locationStack = useLocationStack();

    // Attempt to auto detect id
    const pressableId = makeId(
      id ?? nativeProps.id ?? nativeProps.title ?? makeTitleFromChildren(nativeProps.children),
      normalizeId
    );

    // Prepare new Component props
    const componentProps = {
      ...nativeProps,
      ...(ref ? { ref } : {}),
    };

    // If we couldn't generate an `id`, log the issue and return an untracked Component.
    if (!pressableId) {
      if (globalThis.objectiv.devTools) {
        const locationPath = globalThis.objectiv.devTools.getLocationPath(locationStack);
        globalThis.objectiv.devTools.TrackerConsole.error(
          `｢objectiv｣ Could not generate a valid id for PressableContext @ ${locationPath}. Please provide either the \`title\` or the \`objectiv.id\` property manually.`
        );
      }
      return <Component {...componentProps} />;
    }

    // Wrap Component in PressableContextWrapper
    return (
      <PressableContextWrapper id={pressableId}>
        {(trackingContext) => (
          <Component
            {...componentProps}
            onClick={(event: React.MouseEvent) => {
              // Track click as PressEvent
              trackPressEvent(trackingContext);

              // If present, execute also onClick prop
              props.onClick && props.onClick(event);
            }}
          />
        )}
      </PressableContextWrapper>
    );
  }
) as <T>(props: PropsWithRef<TrackedPressableContextProps<T>>) => JSX.Element;
