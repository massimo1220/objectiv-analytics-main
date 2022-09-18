/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeId } from '@objectiv/tracker-core';
import { ExpandableContextWrapper, trackVisibility, useLocationStack } from '@objectiv/tracker-react-core';
import React, { forwardRef, PropsWithRef, Ref, useRef } from 'react';
import { TrackedShowableContextProps } from '../types';

/**
 * Generates a new React Element already wrapped in an ExpandableContext.
 * Automatically tracks HiddenEvent and VisibleEvent based on the given `isVisible` prop.
 */
export const TrackedExpandableContext = forwardRef(
  <T extends unknown>(props: TrackedShowableContextProps<T>, ref: Ref<unknown>) => {
    const {
      objectiv: { id, Component, isVisible = false, normalizeId = true },
      ...nativeProps
    } = props;
    const wasVisible = useRef<boolean>(isVisible);
    const locationStack = useLocationStack();

    // Attempt to auto detect id
    const expandableId = makeId(id ?? nativeProps.id, normalizeId);

    const componentProps = {
      ...nativeProps,
      ...(ref ? { ref } : {}),
    };

    if (!expandableId) {
      if (globalThis.objectiv.devTools) {
        const locationPath = globalThis.objectiv.devTools.getLocationPath(locationStack);
        globalThis.objectiv.devTools.TrackerConsole.error(
          `｢objectiv｣ Could not generate a valid id for ExpandableContext @ ${locationPath}. Please provide the \`objectiv.id\` property.`
        );
      }

      return <Component {...componentProps} />;
    }

    return (
      <ExpandableContextWrapper id={expandableId}>
        {(trackingContext) => {
          if ((wasVisible.current && !isVisible) || (!wasVisible.current && isVisible)) {
            wasVisible.current = isVisible;
            trackVisibility({ isVisible, ...trackingContext });
          }

          return <Component {...componentProps} />;
        }}
      </ExpandableContextWrapper>
    );
  }
) as <T>(props: PropsWithRef<TrackedShowableContextProps<T>>) => JSX.Element;
