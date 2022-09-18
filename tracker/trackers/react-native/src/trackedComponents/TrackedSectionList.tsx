/*
 * Copyright 2022 Objectiv B.V.
 */

import { ContentContextWrapper } from '@objectiv/tracker-react-core';
import React from 'react';
import { DefaultSectionT, SectionList, SectionListProps } from 'react-native';

/**
 * TrackedSectionList has the same props of SectionList with an additional required `id` prop.
 */
export type TrackedSectionListProps<ItemT, SectionT = DefaultSectionT> = SectionListProps<ItemT, SectionT> & {
  /**
   * The ContentContext `id`.
   */
  id: string;
};

/**
 * A SectionList already wrapped in ContentContext.
 */
export function TrackedSectionList<ItemT, SectionT = DefaultSectionT>(props: TrackedSectionListProps<ItemT, SectionT>) {
  const { id, ...sectionListProps } = props;

  return (
    <ContentContextWrapper id={id}>
      <SectionList {...sectionListProps} />
    </ContentContextWrapper>
  );
}
