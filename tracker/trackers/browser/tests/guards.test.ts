/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import {
  isParentTaggedElement,
  isTagChildrenElement,
  isTaggableElement,
  isTaggedElement,
  isWaitUntilTrackedOptions,
  TaggingAttribute,
} from '../src';

describe('isTaggableElement', () => {
  it('should return false', () => {
    expect(isTaggableElement(document.createComment('some comment'))).toBe(false);
    expect(isTaggableElement(document.createTextNode('some text'))).toBe(false);
    expect(isTaggableElement(document.createDocumentFragment())).toBe(false);

    // TODO cover negative cases
  });

  it('should return true', () => {
    // Some HTMLElements
    expect(isTaggableElement(document.createElement('html'))).toBe(true);
    expect(isTaggableElement(document.createElement('head'))).toBe(true);
    expect(isTaggableElement(document.createElement('body'))).toBe(true);
    expect(isTaggableElement(document.createElement('title'))).toBe(true);
    expect(isTaggableElement(document.createElement('h1'))).toBe(true);
    expect(isTaggableElement(document.createElement('h2'))).toBe(true);
    expect(isTaggableElement(document.createElement('h3'))).toBe(true);
    expect(isTaggableElement(document.createElement('h4'))).toBe(true);
    expect(isTaggableElement(document.createElement('h5'))).toBe(true);
    expect(isTaggableElement(document.createElement('h6'))).toBe(true);
    expect(isTaggableElement(document.createElement('p'))).toBe(true);
    expect(isTaggableElement(document.createElement('em'))).toBe(true);
    expect(isTaggableElement(document.createElement('i'))).toBe(true);
    expect(isTaggableElement(document.createElement('b'))).toBe(true);
    expect(isTaggableElement(document.createElement('small'))).toBe(true);
    expect(isTaggableElement(document.createElement('strong'))).toBe(true);
    expect(isTaggableElement(document.createElement('u'))).toBe(true);
    expect(isTaggableElement(document.createElement('strike'))).toBe(true);
    expect(isTaggableElement(document.createElement('div'))).toBe(true);
    expect(isTaggableElement(document.createElement('button'))).toBe(true);
    expect(isTaggableElement(document.createElement('a'))).toBe(true);
    expect(isTaggableElement(document.createElement('section'))).toBe(true);
    expect(isTaggableElement(document.createElement('header'))).toBe(true);
    expect(isTaggableElement(document.createElement('nav'))).toBe(true);
    expect(isTaggableElement(document.createElement('main'))).toBe(true);
    expect(isTaggableElement(document.createElement('aside'))).toBe(true);
    expect(isTaggableElement(document.createElement('footer'))).toBe(true);
    expect(isTaggableElement(document.createElement('article'))).toBe(true);
    expect(isTaggableElement(document.createElement('ul'))).toBe(true);
    expect(isTaggableElement(document.createElement('li'))).toBe(true);
    expect(isTaggableElement(document.createElement('ol'))).toBe(true);
    expect(isTaggableElement(document.createElement('br'))).toBe(true);
    expect(isTaggableElement(document.createElement('hr'))).toBe(true);

    // Some SVGElements
    expect(isTaggableElement(document.createElement('circle'))).toBe(true);
    expect(isTaggableElement(document.createElement('line'))).toBe(true);
    expect(isTaggableElement(document.createElement('area'))).toBe(true);

    // TODO cover negative cases
  });
});

describe('isTaggedElement', () => {
  const div = document.createElement('div');
  const section = document.createElement('section');
  const button = document.createElement('button');

  it('should return false', () => {
    expect(isTaggedElement(div)).toBe(false);
    expect(isTaggedElement(section)).toBe(false);
    expect(isTaggedElement(button)).toBe(false);

    // TODO cover negative cases
  });

  it('should return true', () => {
    div.setAttribute(TaggingAttribute.context, 'value');
    expect(isTaggedElement(div)).toBe(true);

    section.setAttribute(TaggingAttribute.context, 'value');
    expect(isTaggedElement(section)).toBe(true);

    button.setAttribute(TaggingAttribute.context, 'value');
    expect(isTaggedElement(button)).toBe(true);

    // TODO cover negative cases
  });
});

describe('isTagChildrenElement', () => {
  const div = document.createElement('div');
  const section = document.createElement('section');
  const button = document.createElement('button');

  it('should return false', () => {
    expect(isTaggedElement(div)).toBe(false);
    expect(isTaggedElement(section)).toBe(false);
    expect(isTaggedElement(button)).toBe(false);

    // TODO cover negative cases
  });

  it('should return true', () => {
    div.setAttribute(TaggingAttribute.tagChildren, '1');
    expect(isTagChildrenElement(div)).toBe(true);

    section.setAttribute(TaggingAttribute.tagChildren, 'value');
    expect(isTagChildrenElement(section)).toBe(true);

    button.setAttribute(TaggingAttribute.tagChildren, 'value');
    expect(isTagChildrenElement(button)).toBe(true);

    // TODO cover negative cases
  });
});

describe('isParentTaggedElement', () => {
  const div = document.createElement('div');
  const section = document.createElement('section');
  const button = document.createElement('button');

  it('should return false', () => {
    expect(isTaggedElement(div)).toBe(false);
    expect(isTaggedElement(section)).toBe(false);
    expect(isTaggedElement(button)).toBe(false);

    // TODO cover negative cases
  });

  it('should return true', () => {
    div.setAttribute(TaggingAttribute.context, 'value');
    div.setAttribute(TaggingAttribute.parentElementId, 'value');
    expect(isParentTaggedElement(div)).toBe(true);

    section.setAttribute(TaggingAttribute.context, 'value');
    section.setAttribute(TaggingAttribute.parentElementId, 'value');
    expect(isParentTaggedElement(section)).toBe(true);

    button.setAttribute(TaggingAttribute.context, 'value');
    button.setAttribute(TaggingAttribute.parentElementId, 'value');
    expect(isParentTaggedElement(button)).toBe(true);

    // TODO cover negative cases
  });
});

describe('isWaitUntilTrackedOptions', () => {
  it('should return false', () => {
    // @ts-ignore
    expect(isWaitUntilTrackedOptions('nope')).toBe(false);
    // @ts-ignore
    expect(isWaitUntilTrackedOptions(null)).toBe(false);
    // @ts-ignore
    expect(isWaitUntilTrackedOptions(undefined)).toBe(false);
    // @ts-ignore
    expect(isWaitUntilTrackedOptions(0)).toBe(false);
    // @ts-ignore
    expect(isWaitUntilTrackedOptions(1)).toBe(false);
    // @ts-ignore
    expect(isWaitUntilTrackedOptions([])).toBe(false);
    // @ts-ignore
    expect(isWaitUntilTrackedOptions({ intervalMs: 'nope' })).toBe(false);
    // @ts-ignore
    expect(isWaitUntilTrackedOptions({ timeoutMs: 'nope' })).toBe(false);
    // @ts-ignore
    expect(isWaitUntilTrackedOptions({ flushQueue: 'nope' })).toBe(false);
  });
});
