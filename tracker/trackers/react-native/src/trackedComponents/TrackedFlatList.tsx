/*
 * Copyright 2022 Objectiv B.V.
 */

import { ContentContextWrapper } from '@objectiv/tracker-react-core';
import React from 'react';
import { FlatList, FlatListProps } from 'react-native';

/**
 * TrackedFlatList has the same props of FlatList with an additional required `id` prop.
 */
export type TrackedFlatListProps<ItemT> = FlatListProps<ItemT> & {
  /**
   * The ContentContext `id`.
   */
  id: string;
};

/**
 * A FlatList already wrapped in ContentContext.
 */
export function TrackedFlatList<ItemT>(props: TrackedFlatListProps<ItemT>) {
  const { id, ...flatListProps } = props;

  return (
    <ContentContextWrapper id={id}>
      <FlatList {...flatListProps} />
    </ContentContextWrapper>
  );
}
