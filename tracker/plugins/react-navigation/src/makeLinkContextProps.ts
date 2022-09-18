/*
 * Copyright 2022 Objectiv B.V.
 */

import { makeId } from '@objectiv/tracker-core';
import { makeTitleFromChildren } from '@objectiv/tracker-react-core';
import { getPathFromState } from '@react-navigation/native';
import { TrackedLinkProps } from './TrackedLink';

/**
 * A helper method to generate LinkContext `id` and `href` props from TrackedLink `to` and `children` props.
 */
export function makeLinkContextProps<ParamList extends ReactNavigation.RootParamList>(
  props: TrackedLinkProps<ParamList>
) {
  // Either use the given id or attempt to auto-detect `id` for LinkContext by looking at the `children` prop.
  const title = makeTitleFromChildren(props.children);
  const contextId = props.id ?? makeId(title);

  // Use React Navigation `getPathFromState` to generate the `href` prop. Unless it was already a string.
  let contextHref: string;
  if (typeof props.to === 'string') {
    contextHref = props.to as string;
  } else {
    contextHref = getPathFromState({
      routes: [
        {
          name: props.to.screen,
          params: props.to.params as {},
        },
      ],
    });
  }

  return {
    contextId,
    contextHref,
  };
}
