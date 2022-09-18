/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { ValidateAttribute } from '../../definitions/ValidateAttribute';
import { isValidateAttribute } from '../guards/isValidateAttribute';
import { stringifyJson } from './stringifyJson';

/**
 * `validate` Tagging Attribute stringifier
 */
export const stringifyValidate = (validateAttribute: ValidateAttribute) => {
  if (!isValidateAttribute(validateAttribute)) {
    throw new Error(`validate attribute is not valid, received: ${JSON.stringify(validateAttribute)}`);
  }

  return stringifyJson(validateAttribute);
};
