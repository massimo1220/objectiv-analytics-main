/*
 * Copyright 2022 Objectiv B.V.
 */

import { ContentContextWrapper } from '@objectiv/tracker-react-core';
import React from 'react';
import { VirtualizedList, VirtualizedListProps } from 'react-native';

/**
 * TrackedVirtualizedList has the same props of VirtualizedList with an additional required `id` prop.
 */
export type TrackedVirtualizedListProps<ItemT> = VirtualizedListProps<ItemT> & {
  /**
   * The ContentContext `id`.
   */
  id: string;
};

/**
 * A VirtualizedList already wrapped in ContentContext.
 */
export function TrackedVirtualizedList<ItemT>(props: TrackedVirtualizedListProps<ItemT>) {
  const { id, ...virtualizedListProps } = props;

  return (
    <ContentContextWrapper id={id}>
      <VirtualizedList {...virtualizedListProps} />
    </ContentContextWrapper>
  );
}
