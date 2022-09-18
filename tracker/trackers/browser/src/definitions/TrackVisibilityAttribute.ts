/*
 * Copyright 2021-2022 Objectiv B.V.
 */

/**
 * The definition of the `trackVisibility` Tagging Attribute
 */
export type TrackVisibilityAttribute = boolean | { mode: 'auto' } | { mode: 'manual'; isVisible: boolean };
