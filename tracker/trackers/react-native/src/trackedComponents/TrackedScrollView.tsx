/*
 * Copyright 2022 Objectiv B.V.
 */

import { ContentContextWrapper } from '@objectiv/tracker-react-core';
import React from 'react';
import { ScrollView, ScrollViewProps } from 'react-native';

/**
 * TrackedScrollView has the same props of ScrollView with an additional required `id` prop.
 */
export type TrackedScrollViewProps = ScrollViewProps & {
  /**
   * The ContentContext `id`.
   */
  id: string;
};

/**
 * A ScrollView already wrapped in ContentContext.
 */
export function TrackedScrollView(props: TrackedScrollViewProps) {
  const { id, ...scrollViewProps } = props;

  return (
    <ContentContextWrapper id={id}>
      <ScrollView {...scrollViewProps} />
    </ContentContextWrapper>
  );
}
