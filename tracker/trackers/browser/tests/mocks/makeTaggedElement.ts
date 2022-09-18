/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makePressableContext, makeInputContext, makeContentContext } from '@objectiv/tracker-core';
import { stringifyLocationContext, TaggedElement, TaggingAttribute } from '../../src';

export const makeTaggedElement = (
  id: string,
  contextId: string | null,
  tagName: keyof HTMLElementTagNameMap,
  trackClicks?: boolean,
  trackBlurs?: boolean
): TaggedElement => {
  const trackedDiv = document.createElement(tagName);

  trackedDiv.setAttribute(TaggingAttribute.elementId, id);

  if (contextId && trackClicks) {
    trackedDiv.setAttribute(
      TaggingAttribute.context,
      stringifyLocationContext(makePressableContext({ id: contextId }))
    );
  } else if (contextId && trackBlurs) {
    trackedDiv.setAttribute(TaggingAttribute.context, stringifyLocationContext(makeInputContext({ id: contextId })));
  } else if (contextId) {
    trackedDiv.setAttribute(TaggingAttribute.context, stringifyLocationContext(makeContentContext({ id: contextId })));
  }

  if (trackClicks) {
    trackedDiv.setAttribute(TaggingAttribute.trackClicks, 'true');
  }

  if (trackBlurs) {
    trackedDiv.setAttribute(TaggingAttribute.trackBlurs, 'true');
  }

  return trackedDiv as TaggedElement;
};
