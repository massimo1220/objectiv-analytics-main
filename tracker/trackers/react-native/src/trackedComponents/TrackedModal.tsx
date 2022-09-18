/*
 * Copyright 2022 Objectiv B.V.
 */

import { OverlayContextWrapper, useHiddenEventTracker, useVisibleEventTracker } from '@objectiv/tracker-react-core';
import React, { useEffect, useState } from 'react';
import { Modal, ModalProps } from 'react-native';

/**
 * TrackedModal has the same props of Modal with an additional required `id` prop.
 */
export type TrackedModalProps = ModalProps & {
  /**
   * The OverlayContext `id`.
   */
  id: string;
};

/**
 * A Modal already wrapped in OverlayContext automatically tracking VisibleEvent and HiddenEvent.
 */
export function TrackedModal(props: TrackedModalProps) {
  const { id, ...modalProps } = props;
  const [previousVisibleState, setPreviousVisibleState] = useState(props.visible);

  const WrappedModal = (props: ModalProps) => {
    const trackVisibleEvent = useVisibleEventTracker();
    const trackHiddenEvent = useHiddenEventTracker();

    useEffect(() => {
      if (props.visible === undefined || previousVisibleState === undefined) {
        return;
      }

      if (props.visible === previousVisibleState) {
        return;
      }

      if (props.visible) {
        trackVisibleEvent();
      } else {
        trackHiddenEvent();
      }

      setPreviousVisibleState(props.visible);
    }, [props.visible]);

    return <Modal {...props} />;
  };

  return (
    <OverlayContextWrapper id={id}>
      <WrappedModal {...modalProps} />
    </OverlayContextWrapper>
  );
}
