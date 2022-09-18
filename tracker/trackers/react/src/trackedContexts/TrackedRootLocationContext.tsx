/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeId } from '@objectiv/tracker-core';
import { RootLocationContextWrapper } from '@objectiv/tracker-react-core';
import React, { forwardRef, PropsWithRef, Ref } from 'react';
import { TrackedContextProps } from '../types';

/**
 * Generates a new React Element already wrapped in a RootLocationContext.
 */
export const TrackedRootLocationContext = forwardRef(
  <T extends unknown>(props: TrackedContextProps<T>, ref: Ref<unknown>) => {
    const {
      objectiv: { Component, id, normalizeId = true },
      ...nativeProps
    } = props;

    // Attempt to auto detect id
    const rootId = makeId(id ?? nativeProps.id, normalizeId);

    const componentProps = {
      ...nativeProps,
      ...(ref ? { ref } : {}),
    };

    if (!rootId) {
      if (globalThis.objectiv.devTools) {
        globalThis.objectiv.devTools.TrackerConsole.error(
          `｢objectiv｣ Could not generate a valid id for RootLocationContext. Please provide the \`objectiv.id\` property.`
        );
      }

      return <Component {...componentProps} />;
    }

    return (
      <RootLocationContextWrapper id={rootId}>
        <Component {...componentProps} />
      </RootLocationContextWrapper>
    );
  }
) as <T>(props: PropsWithRef<TrackedContextProps<T>>) => JSX.Element;
