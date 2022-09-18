/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { TaggableElement } from './TaggableElement';

/**
 * A TrackedElement is either a TaggedElement or an EventTarget
 */
export type TrackedElement = TaggableElement | EventTarget;
