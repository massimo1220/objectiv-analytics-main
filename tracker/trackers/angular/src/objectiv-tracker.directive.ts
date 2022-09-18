/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { Directive, ElementRef, Input } from '@angular/core';
import {
  ChildrenTaggingQueries,
  ChildrenTaggingQuery,
  LocationTaggerParameters,
  tagChild,
  tagChildren,
  TagChildrenReturnValue,
  tagContent,
  tagExpandable,
  tagInput,
  tagLink,
  TagLinkParameters,
  tagLocation,
  TagLocationParameters,
  TagLocationReturnValue,
  tagMediaPlayer,
  tagNavigation,
  tagOverlay,
  tagPressable,
  tagRootLocation,
} from '@objectiv/tracker-browser';

/**
 * Allows calling Browser Tracker Location Taggers and Children Taggers directly from templates
 */
@Directive({
  selector:
    '[applyTaggingAttributes], [tagChild], [tagChildren], [tagContent], [tagExpandable], [tagInput], [tagLink], [tagLocation], [tagMediaPlayer], [tagNavigation], [tagOverlay], [tagPressable], [tagRootLocation]',
})
export class ObjectivTrackerDirective {
  @Input() applyTaggingAttributes: TagLocationReturnValue;
  @Input() tagChild: ChildrenTaggingQuery;
  @Input() tagChildren: ChildrenTaggingQueries;
  @Input() tagContent: LocationTaggerParameters;
  @Input() tagExpandable: LocationTaggerParameters;
  @Input() tagInput: LocationTaggerParameters;
  @Input() tagLink: TagLinkParameters;
  @Input() tagLocation: TagLocationParameters;
  @Input() tagMediaPlayer: LocationTaggerParameters;
  @Input() tagNavigation: LocationTaggerParameters;
  @Input() tagOverlay: LocationTaggerParameters;
  @Input() tagPressable: LocationTaggerParameters;
  @Input() tagRootLocation: LocationTaggerParameters;

  constructor(public element: ElementRef<HTMLElement>) {}

  ngOnInit() {
    let locationTaggingAttributes: TagLocationReturnValue;
    let childrenTaggingAttributes: TagChildrenReturnValue;

    // Children / Child Tagger
    if (this.tagChildren) {
      childrenTaggingAttributes = tagChildren(this.tagChildren);
    } else if (this.tagChild) {
      childrenTaggingAttributes = tagChild(this.tagChild);
    }

    // Location Taggers
    if (this.tagContent) {
      locationTaggingAttributes = tagContent(this.tagContent);
    } else if (this.tagExpandable) {
      locationTaggingAttributes = tagExpandable(this.tagExpandable);
    } else if (this.tagInput) {
      locationTaggingAttributes = tagInput(this.tagInput);
    } else if (this.tagLink) {
      locationTaggingAttributes = tagLink(this.tagLink);
    } else if (this.tagLocation) {
      locationTaggingAttributes = tagLocation(this.tagLocation);
    } else if (this.tagMediaPlayer) {
      locationTaggingAttributes = tagMediaPlayer(this.tagMediaPlayer);
    } else if (this.tagNavigation) {
      locationTaggingAttributes = tagNavigation(this.tagNavigation);
    } else if (this.tagOverlay) {
      locationTaggingAttributes = tagOverlay(this.tagOverlay);
    } else if (this.tagPressable) {
      locationTaggingAttributes = tagPressable(this.tagPressable);
    } else if (this.tagRootLocation) {
      locationTaggingAttributes = tagRootLocation(this.tagRootLocation);
    }

    // Merge Location Tagging Attributes and Children Tagging Attributes
    const taggingAttributes = {
      ...(this.applyTaggingAttributes ?? {}),
      ...(locationTaggingAttributes ?? {}),
      ...(childrenTaggingAttributes ?? {}),
    };

    // Set all attributes on the nativeElement
    for (let [key, value] of Object.entries<string | undefined>(taggingAttributes)) {
      if (value !== undefined) {
        this.element.nativeElement.setAttribute(key, value);
      }
    }
  }
}
