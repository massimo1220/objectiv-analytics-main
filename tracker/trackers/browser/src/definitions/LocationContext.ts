/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import {
  ContentContext,
  ExpandableContext,
  InputContext,
  LinkContext,
  MediaPlayerContext,
  NavigationContext,
  OverlayContext,
  PressableContext,
  RootLocationContext,
} from '@objectiv/schema';

export type AnyLocationContext =
  | ContentContext
  | ExpandableContext
  | InputContext
  | LinkContext
  | MediaPlayerContext
  | NavigationContext
  | OverlayContext
  | PressableContext
  | RootLocationContext;

/**
 * Union to match any PressableContext
 */
export type AnyPressableContext = LinkContext | PressableContext;

/**
 * Union to match any Showable Context, that is Overlays and ExpandableContext
 */
export type AnyShowableContext = OverlayContext | ExpandableContext;
