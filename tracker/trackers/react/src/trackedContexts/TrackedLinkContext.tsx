/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeId } from '@objectiv/tracker-core';
import { LinkContextWrapper, makeTitleFromChildren, useLocationStack } from '@objectiv/tracker-react-core';
import React, { forwardRef, PropsWithRef, Ref } from 'react';
import { makeAnchorClickHandler } from '../common/factories/makeAnchorClickHandler';
import { TrackedLinkContextProps } from '../types';

/**
 * Generates a new React Element already wrapped in an LinkContext.
 * Automatically tracks PressEvent when the given Component receives an `onClick` SyntheticEvent.
 */
export const TrackedLinkContext = forwardRef(
  <T extends unknown>(props: TrackedLinkContextProps<T>, ref: Ref<unknown>) => {
    const {
      objectiv: { Component, id, href, normalizeId = true, waitUntilTracked = false },
      ...nativeProps
    } = props;

    // Attempt to auto-detect `id`
    const linkId = makeId(
      id ?? nativeProps.id ?? nativeProps.title ?? makeTitleFromChildren(props.children),
      normalizeId
    );

    // Attempt to auto-detect `href`
    const linkHref = href ?? nativeProps.href;

    const componentProps = {
      ...nativeProps,
      ...(ref ? { ref } : {}),
    };

    const locationStack = useLocationStack();
    if (!linkId || !linkHref) {
      if (globalThis.objectiv.devTools) {
        const locationPath = globalThis.objectiv.devTools.getLocationPath(locationStack);

        if (!linkId) {
          globalThis.objectiv.devTools.TrackerConsole.error(
            `｢objectiv｣ Could not generate a valid id for LinkContext @ ${locationPath}. Please provide either the \`title\` or the \`objectiv.id\` property manually.`
          );
        }

        if (!linkHref) {
          globalThis.objectiv.devTools.TrackerConsole.error(
            `｢objectiv｣ Could not generate a valid href for LinkContext @ ${locationPath}. Please provide the \`objectiv.href\` property manually.`
          );
        }
      }

      return <Component {...componentProps} />;
    }

    return (
      <LinkContextWrapper id={linkId} href={linkHref}>
        {(trackingContext) => (
          <Component
            {...componentProps}
            onClick={makeAnchorClickHandler({
              trackingContext,
              anchorHref: linkHref,
              waitUntilTracked,
              onClick: nativeProps.onClick,
            })}
          />
        )}
      </LinkContextWrapper>
    );
  }
) as <T>(props: PropsWithRef<TrackedLinkContextProps<T>>) => JSX.Element;
