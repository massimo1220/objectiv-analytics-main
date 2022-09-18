/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeRootLocationContext } from '@objectiv/tracker-core';
import { isLocationTaggerParameters } from '../common/guards/isLocationTaggerParameters';
import { trackerErrorHandler } from '../common/trackerErrorHandler';
import { LocationTaggerParameters } from '../definitions/LocationTaggerParameters';
import { TagLocationReturnValue } from '../definitions/TagLocationReturnValue';
import { tagLocation } from './tagLocation';

/**
 * tagRootLocation is a shorthand for tagLocation. It eases the tagging of RootLocationContext bound Elements.
 */
export const tagRootLocation = (parameters: LocationTaggerParameters): TagLocationReturnValue => {
  try {
    if (!isLocationTaggerParameters(parameters)) {
      throw new Error(`Invalid location tagger parameters: ${JSON.stringify(parameters)}`);
    }
    const { id, options } = parameters;
    return tagLocation({ instance: makeRootLocationContext({ id }), options, onError: parameters.onError });
  } catch (error) {
    return trackerErrorHandler(error, parameters);
  }
};
