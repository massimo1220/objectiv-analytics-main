/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { isValidateAttribute } from '../guards/isValidateAttribute';
import { parseJson } from './parseJson';

/**
 * `validate` Tagging Attribute parser
 */
export const parseValidate = (stringifiedValidateAttribute: string | null) => {
  if (!stringifiedValidateAttribute) {
    return {
      locationUniqueness: true,
    };
  }

  const validateAttribute = parseJson(stringifiedValidateAttribute);

  if (!isValidateAttribute(validateAttribute)) {
    throw new Error(`validate attribute is not valid: ${JSON.stringify(stringifiedValidateAttribute)}`);
  }

  return validateAttribute;
};
