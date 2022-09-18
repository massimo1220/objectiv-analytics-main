/*
 * Copyright 2022 Objectiv B.V.
 */

import { ContentContextWrapper } from '@objectiv/tracker-react-core';
import React from 'react';
import { SafeAreaView, ViewProps } from 'react-native';

/**
 * TrackedSafeAreaView has the same props of SafeAreaView with the addition of a required `id` prop.
 */
export type TrackedSafeAreaViewProps = ViewProps & {
  /**
   * The ContentContext `id`.
   */
  id: string;
};

/**
 * A SafeAreaView already wrapped in ContentContext.
 */
export function TrackedSafeAreaView(props: TrackedSafeAreaViewProps) {
  const { id, ...viewProps } = props;

  return (
    <ContentContextWrapper id={id}>
      <SafeAreaView {...viewProps} />
    </ContentContextWrapper>
  );
}
