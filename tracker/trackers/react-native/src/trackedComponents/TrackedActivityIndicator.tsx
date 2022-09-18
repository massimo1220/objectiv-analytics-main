/*
 * Copyright 2022 Objectiv B.V.
 */

import { OverlayContextWrapper, useHiddenEventTracker, useVisibleEventTracker } from '@objectiv/tracker-react-core';
import React, { useEffect, useState } from 'react';
import { ActivityIndicator, ActivityIndicatorProps } from 'react-native';

/**
 * TrackedActivityIndicator has the same props of ActivityIndicator with an additional required `id` prop.
 */
export type TrackedActivityIndicatorProps = ActivityIndicatorProps & {
  /**
   * The OverlayContext `id`.
   */
  id: string;
};

/**
 * An ActivityIndicator already wrapped in OverlayContext automatically tracking VisibleEvent and HiddenEvent.
 */
export function TrackedActivityIndicator(props: TrackedActivityIndicatorProps) {
  const { id, ...modalProps } = props;
  const [previousAnimatingState, setPreviousAnimatingState] = useState(props.animating);

  const WrappedActivityIndicator = (props: ActivityIndicatorProps) => {
    const trackVisibleEvent = useVisibleEventTracker();
    const trackHiddenEvent = useHiddenEventTracker();

    useEffect(() => {
      if (props.animating === undefined || previousAnimatingState === undefined) {
        return;
      }

      if (props.animating === previousAnimatingState) {
        return;
      }

      if (props.animating) {
        trackVisibleEvent();
      } else {
        trackHiddenEvent();
      }

      setPreviousAnimatingState(props.animating);
    }, [props.animating]);

    return <ActivityIndicator {...props} />;
  };

  return (
    <OverlayContextWrapper id={id}>
      <WrappedActivityIndicator {...modalProps} />
    </OverlayContextWrapper>
  );
}
