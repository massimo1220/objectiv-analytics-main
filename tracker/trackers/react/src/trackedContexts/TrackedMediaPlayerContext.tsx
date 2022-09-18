/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeId } from '@objectiv/tracker-core';
import { MediaPlayerContextWrapper, useLocationStack } from '@objectiv/tracker-react-core';
import React, { forwardRef, PropsWithRef, Ref } from 'react';
import { TrackedContextProps } from '../types';

/**
 * Generates a new React Element already wrapped in a MediaPlayerContext.
 */
export const TrackedMediaPlayerContext = forwardRef(
  <T extends unknown>(props: TrackedContextProps<T>, ref: Ref<unknown>) => {
    const {
      objectiv: { Component, id, normalizeId = true },
      ...nativeProps
    } = props;
    const locationStack = useLocationStack();

    // Attempt to auto detect id
    const mediaPlayerId = makeId(id ?? nativeProps.id, normalizeId);

    const componentProps = {
      ...nativeProps,
      ...(ref ? { ref } : {}),
    };

    if (!mediaPlayerId) {
      if (globalThis.objectiv.devTools) {
        const locationPath = globalThis.objectiv.devTools.getLocationPath(locationStack);
        globalThis.objectiv.devTools.TrackerConsole.error(
          `｢objectiv｣ Could not generate a valid id for MediaPlayerContext @ ${locationPath}. Please provide the \`objectiv.id\` property.`
        );
      }
      return <Component {...componentProps} />;
    }

    return (
      <MediaPlayerContextWrapper id={mediaPlayerId}>
        <Component {...componentProps} />
      </MediaPlayerContextWrapper>
    );
  }
) as <T>(props: PropsWithRef<TrackedContextProps<T>>) => JSX.Element;
