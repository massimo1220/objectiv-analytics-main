/*
 * Copyright 2022 Objectiv B.V.
 */

import { ChangeEvent, FocusEvent, MouseEvent, SyntheticEvent } from 'react';

/**
 * A type guard to determine whether the given event is a blur event
 */
export function isBlurEvent<T = HTMLInputElement | HTMLSelectElement>(
  event: SyntheticEvent<T>
): event is FocusEvent<T> {
  return event.type === 'blur';
}

/**
 * A type guard to determine whether the given event is a change event
 */
export function isChangeEvent<T = HTMLInputElement | HTMLSelectElement>(
  event: SyntheticEvent<T>
): event is ChangeEvent<T> {
  return event.type === 'change';
}

/**
 * A type guard to determine whether the given event is a click event
 */
export function isClickEvent<T = HTMLInputElement | HTMLSelectElement>(
  event: SyntheticEvent<T>
): event is MouseEvent<T> {
  return event.type === 'click';
}

/**
 * Helper function to parse the value of the monitored attribute.
 * Ensures the result is a string and normalizes booleans to '0' and '1'
 */
export const normalizeValue = (value?: unknown) => {
  if (typeof value === 'string') {
    return value;
  }

  if (typeof value === 'boolean') {
    return value ? '1' : '0';
  }

  if (typeof value === 'number') {
    return value.toString();
  }

  if (Array.isArray(value)) {
    return JSON.stringify(value);
  }

  return '';
};
