/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { makeMediaPlayerContext } from '@objectiv/tracker-core';
import { isLocationTaggerParameters } from '../common/guards/isLocationTaggerParameters';
import { trackerErrorHandler } from '../common/trackerErrorHandler';
import { LocationTaggerParameters } from '../definitions/LocationTaggerParameters';
import { TagLocationReturnValue } from '../definitions/TagLocationReturnValue';
import { tagLocation } from './tagLocation';

/**
 * tagMediaPlayer is a shorthand for tagLocation. It eases the tagging of MediaPlayerContext bound Elements
 */
export const tagMediaPlayer = (parameters: LocationTaggerParameters): TagLocationReturnValue => {
  try {
    if (!isLocationTaggerParameters(parameters)) {
      throw new Error(`Invalid location tagger parameters: ${JSON.stringify(parameters)}`);
    }
    const { id, options } = parameters;
    return tagLocation({ instance: makeMediaPlayerContext({ id }), options, onError: parameters.onError });
  } catch (error) {
    return trackerErrorHandler(error, parameters);
  }
};
