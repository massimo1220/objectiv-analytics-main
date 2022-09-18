/*
 * Copyright 2022 Objectiv B.V.
 */

import { ContentContextWrapper } from '@objectiv/tracker-react-core';
import React from 'react';
import { KeyboardAvoidingView, KeyboardAvoidingViewProps } from 'react-native';

/**
 * TrackedKeyboardAvoidingView has the same props of KeyboardAvoidingView with the addition of a required `id` prop.
 */
export type TrackedKeyboardAvoidingViewProps = KeyboardAvoidingViewProps & {
  /**
   * The ContentContext `id`.
   */
  id: string;
};

/**
 * A KeyboardAvoidingView already wrapped in ContentContext.
 */
export function TrackedKeyboardAvoidingView(props: TrackedKeyboardAvoidingViewProps) {
  const { id, ...viewProps } = props;

  return (
    <ContentContextWrapper id={id}>
      <KeyboardAvoidingView {...viewProps} />
    </ContentContextWrapper>
  );
}
