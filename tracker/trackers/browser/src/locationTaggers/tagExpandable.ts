/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeExpandableContext } from '@objectiv/tracker-core';
import { isLocationTaggerParameters } from '../common/guards/isLocationTaggerParameters';
import { trackerErrorHandler } from '../common/trackerErrorHandler';
import { LocationTaggerParameters } from '../definitions/LocationTaggerParameters';
import { TagLocationReturnValue } from '../definitions/TagLocationReturnValue';
import { tagLocation } from './tagLocation';

/**
 * tagExpandable is a shorthand for tagLocation. It eases the tagging of ExpandableContext bound Elements
 */
export const tagExpandable = (parameters: LocationTaggerParameters): TagLocationReturnValue => {
  try {
    if (!isLocationTaggerParameters(parameters)) {
      throw new Error(`Invalid location tagger parameters: ${JSON.stringify(parameters)}`);
    }
    const { id, options } = parameters;
    return tagLocation({ instance: makeExpandableContext({ id }), options, onError: parameters.onError });
  } catch (error) {
    return trackerErrorHandler(error, parameters);
  }
};
