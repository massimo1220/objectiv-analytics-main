/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { ComponentProps, ElementType, MouseEventHandler, PropsWithChildren, ReactHTML } from 'react';

/**
 * Props to specify Component and componentRef to a TrackedContext.
 */
export type ObjectivComponentProp = {
  /**
   * Either an Element or a JSX tag, such as 'div', 'input', etc.
   */
  Component: ElementType | keyof ReactHTML;
};

/**
 * Props to specify tracking id related options to a TrackedContext.
 */
export type ObjectivIdProps = {
  /**
   * The identifier of the LocationContext
   */
  id?: string;

  /**
   * Optional. Default to `true`. Whether to normalize the given id.
   */
  normalizeId?: boolean;
};

/**
 * Props to specify tracking visibility related options to a TrackedContext.
 */
export type ObjectivVisibilityProps = {
  /**
   * Whether to track visibility events automatically when this prop changes state.
   */
  isVisible?: boolean;
};

/**
 * Props to specify tracking link related options to a LinkContext.
 */
export type ObjectivLinkContextProps = {
  /**
   * The destination of this link, required by LinkContext
   */
  href?: string;

  /**
   * Whether to block and wait for the Tracker having sent the event. Eg: a button redirecting to a new location.
   */
  waitUntilTracked?: boolean;
};

/**
 * These props allow configuring how values are tracked for TrackedInputContext and derived Tracked Elements.
 */
export type ObjectivValueTrackingProps = {
  /**
   * Optional. Whether to track the 'value' attribute. Default to false.
   * When enabled, an InputValueContext will be pushed into the Global Contexts of the InputChangeEvent.
   */
  trackValue?: boolean;

  /**
   * Optional. Whether to trigger events only when values actually changed. Default to false.
   * For example, this allows tracking tabbing (e.g. onBlur and value did not change), which is normally prevented.
   */
  stateless?: boolean;

  /**
   * Optional. Which event handler to use. Default is 'onBlur'.
   * Valid values: `onBlur`, `onChange` or `onClick`.
   */
  eventHandler?: 'onBlur' | 'onChange' | 'onClick';
};

/**
 * These props are common to all TrackedContexts.
 */
export type NativeCommonProps = PropsWithChildren<Partial<Pick<HTMLElement, 'id' | 'title'>>>;

/**
 * These props are common to all pressables, e.g. button and anchors.
 */
export type NativePressableCommonProps = NativeCommonProps & {
  onClick?: MouseEventHandler;
};

/**
 * These props are common to all links, e.g. anchors.
 */
export type NativeLinkCommonProps = NativePressableCommonProps & Partial<Pick<HTMLAnchorElement, 'href'>>;

/**
 * Base props of all TrackedContexts.
 */
export type TrackedContextObjectivProp = ObjectivComponentProp & ObjectivIdProps;
export type TrackedContextProps<T, O = TrackedContextObjectivProp> = T &
  NativeCommonProps & {
    objectiv: O;
  };

/**
 * The props of TrackedLinkContext. Extends TrackedContextProps with LinkContext specific properties.
 */
export type TrackedLinkContextObjectivProp = ObjectivComponentProp & ObjectivIdProps & ObjectivLinkContextProps;
export type TrackedLinkContextProps<T, O = TrackedLinkContextObjectivProp> = T &
  NativeLinkCommonProps & {
    objectiv: O;
  };

/**
 * The props of TrackedContexts supporting Visibility events. Extends TrackedContextProps with then `isVisible` property.
 */
export type TrackedShowableContextObjectivProp = ObjectivComponentProp & ObjectivIdProps & ObjectivVisibilityProps;
export type TrackedShowableContextProps<T, O = TrackedShowableContextObjectivProp> = T &
  NativeCommonProps & {
    objectiv: O;
  };

/**
 * The props of TrackedPressableContext. Extends TrackedContextProps with extra pressable related properties.
 */
export type TrackedPressableContextObjectivProp = ObjectivComponentProp & ObjectivIdProps;
export type TrackedPressableContextProps<T, O = TrackedPressableContextObjectivProp> = T &
  NativePressableCommonProps & {
    objectiv: O;
  };

/**
 * Base props of all TrackedElements. They don't include ComponentProp, as we hard-code that for these components.
 * We also try to auto-detect the identifier from the native `id` property, if present
 */
export type TrackedElementProps<T> = T & {
  objectiv?: ObjectivIdProps;
};

/**
 * Overrides TrackedContextProps to make the objectiv prop and all of its attributes optional.
 */
export type TrackedElementWithOptionalIdProps<T> = T & {
  objectiv?: ObjectivIdProps;
};

/**
 * Props used for TrackedInputs
 */
export type TrackedInputProps = ComponentProps<'input'> & {
  objectiv?: ObjectivIdProps & ObjectivValueTrackingProps;
};

/**
 * Props used for TrackedSelect
 */
export type TrackedSelectProps = ComponentProps<'select'> & {
  objectiv?: ObjectivIdProps & ObjectivValueTrackingProps;
};
