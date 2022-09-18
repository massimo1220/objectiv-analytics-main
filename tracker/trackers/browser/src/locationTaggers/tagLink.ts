/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeLinkContext } from '@objectiv/tracker-core';
import { isLocationTaggerParameters } from '../common/guards/isLocationTaggerParameters';
import { trackerErrorHandler } from '../common/trackerErrorHandler';
import { TagLinkParameters } from '../definitions/TagLinkParameters';
import { TagLocationReturnValue } from '../definitions/TagLocationReturnValue';
import { tagLocation } from './tagLocation';

/**
 * tagLink is a shorthand for tagLocation. It eases the tagging of LinkContext bound Elements
 */
export const tagLink = (parameters: TagLinkParameters): TagLocationReturnValue => {
  try {
    if (!isLocationTaggerParameters(parameters)) {
      throw new Error(`Invalid location tagger parameters: ${JSON.stringify(parameters)}`);
    }
    const { id, href, options } = parameters;
    return tagLocation({ instance: makeLinkContext({ id, href }), options, onError: parameters.onError });
  } catch (error) {
    return trackerErrorHandler(error, parameters);
  }
};
