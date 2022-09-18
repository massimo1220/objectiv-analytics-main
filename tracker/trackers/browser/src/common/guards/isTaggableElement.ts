/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { GuardableElement } from '../../definitions/GuardableElement';
import { TaggableElement } from '../../definitions/TaggableElement';

/**
 * A type guard to determine if a the given Element is an HTMLElement or SVGElement.
 * In general we can only tag Elements supporting dataset attributes.
 */
export const isTaggableElement = (element: GuardableElement): element is TaggableElement =>
  element instanceof HTMLElement || element instanceof SVGElement;
