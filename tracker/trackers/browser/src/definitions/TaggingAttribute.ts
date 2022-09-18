/*
 * Copyright 2021-2022 Objectiv B.V.
 */

/**
 * All the attributes that are added to a DOM Element to make it trackable
 */
export enum TaggingAttribute {
  // A unique identifier used internally to pinpoint to a specific instance of a tagged element
  elementId = 'data-objectiv-element-id',

  // DOM traversing to rebuild Locations is not always possible, eg: Portals. This allows specifying a parent Element.
  parentElementId = 'data-objectiv-parent-element-id',

  // A serialized instance of an Objectiv Context.
  context = 'data-objectiv-context',

  // Track click events for this tagged element.
  trackClicks = 'data-objectiv-track-clicks',

  // Track blur events for this tagged element.
  trackBlurs = 'data-objectiv-track-blurs',

  // Determines how we will track visibility events for this tagged element.
  trackVisibility = 'data-objectiv-track-visibility',

  // A list of serialized ChildrenTaggingQuery objects.
  tagChildren = 'data-objectiv-tag-children',

  // Set to `true` by the Mutation Observer when an Element has been processed for auto-tracking.
  tracked = 'data-objectiv-tracked',

  // Holds validation options. They may be used to disable or configure certain automatic checks.
  validate = 'data-objectiv-validate',
}
