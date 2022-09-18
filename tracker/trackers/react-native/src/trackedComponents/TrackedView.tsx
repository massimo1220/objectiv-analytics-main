/*
 * Copyright 2022 Objectiv B.V.
 */

import { ContentContextWrapper } from '@objectiv/tracker-react-core';
import React from 'react';
import { View, ViewProps } from 'react-native';

/**
 * TrackedView has the same props of View with the addition of a required `id` prop.
 */
export type TrackedViewProps = ViewProps & {
  /**
   * The ContentContext `id`.
   */
  id: string;
};

/**
 * A View already wrapped in ContentContext.
 */
export function TrackedView(props: TrackedViewProps) {
  const { id, ...viewProps } = props;

  return (
    <ContentContextWrapper id={id}>
      <View {...viewProps} />
    </ContentContextWrapper>
  );
}
