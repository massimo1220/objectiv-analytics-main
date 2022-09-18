/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TrackedLinkContext, TrackedLinkContextObjectivProp } from '@objectiv/tracker-react';
import React, { ComponentProps } from 'react';
import { Link, LinkProps, useHref } from 'react-router-dom';

/**
 * An overridden version of TrackedLinkProps with a customized objectiv prop:
 * - No `objectiv.Component` attribute, as it's hard-coded to Link
 * - No `objectiv.href` attribute, as we can retrieve one automatically via the `useHref` hook
 * - The objectiv prop itself is optional as there are no required attributes left
 */
export type TrackedLinkProps = LinkProps & {
  objectiv?: Omit<TrackedLinkContextObjectivProp, 'Component' | 'href'>;
};

/**
 * Wraps Link in a TrackedLinkContext which automatically instruments tracking PressEvent on click.
 */
export const TrackedLink = React.forwardRef<HTMLAnchorElement, TrackedLinkProps>(
  ({ objectiv, ...nativeProps }, ref) => (
    <TrackedLinkContext<ComponentProps<typeof Link>>
      {...nativeProps}
      ref={ref}
      objectiv={{
        ...objectiv,
        Component: Link,
        href: useHref(nativeProps.to),
        waitUntilTracked: objectiv?.waitUntilTracked ?? nativeProps.reloadDocument,
      }}
    />
  )
);
