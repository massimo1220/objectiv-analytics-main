/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { isValidElement, ReactNode } from 'react';

/**
 * Recursively traverses the given ReactNode's children in an attempt to retrieve their texts.
 *
 * String Nodes are returned as is, Number nodes are converted to strings and Array children are recursively processed.
 */
export const recursiveGetTextFromChildren = (children: ReactNode): string | undefined => {
  let text;

  // Return strings as they are
  if (typeof children === 'string') {
    text = children;
  }

  // Parse numbers to decimal strings
  else if (typeof children === 'number') {
    text = children.toString(10);
  }

  // If it's an array, parse each child and then compose a string with all of their texts
  else if (children instanceof Array) {
    text = children.map(recursiveGetTextFromChildren).join(' ');
  }

  // If it's a valid React element, parse its children prop
  else if (isValidElement(children)) {
    text = recursiveGetTextFromChildren(children.props.children);
  }

  return text;
};
