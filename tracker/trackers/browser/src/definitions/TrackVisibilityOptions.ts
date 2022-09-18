/*
 * Copyright 2021-2022 Objectiv B.V.
 */

/**
 * The definition of a parsed `trackVisibility` Tagging Attribute
 */
export type TrackVisibilityOptions = undefined | { mode: 'auto' } | { mode: 'manual'; isVisible: boolean };
