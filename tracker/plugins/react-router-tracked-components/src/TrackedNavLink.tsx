/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TrackedLinkContext, TrackedLinkContextObjectivProp } from '@objectiv/tracker-react';
import React, { ComponentProps } from 'react';
import { NavLink, NavLinkProps, useHref } from 'react-router-dom';

/**
 * An overridden version of TrackedLinkProps with a customized objectiv prop:
 * - No `objectiv.Component` attribute, as it's hard-coded to NavLink
 * - No `objectiv.href` attribute, as we can retrieve one automatically via the `useHref` hook
 * - The objectiv prop itself is optional as there are no required attributes left
 */
export type TrackedNavLinkProps = NavLinkProps & {
  objectiv?: Omit<TrackedLinkContextObjectivProp, 'Component' | 'href'>;
};

/**
 * Wraps NavLink in a LinkContext and automatically instruments tracking PressEvent on click.
 */
export const TrackedNavLink = React.forwardRef<HTMLAnchorElement, TrackedNavLinkProps>(
  ({ objectiv, ...nativeProps }, ref) => (
    <TrackedLinkContext<ComponentProps<typeof NavLink>>
      {...nativeProps}
      ref={ref}
      objectiv={{
        ...objectiv,
        Component: NavLink,
        href: useHref(nativeProps.to),
        waitUntilTracked: objectiv?.waitUntilTracked ?? nativeProps.reloadDocument,
      }}
    />
  )
);
