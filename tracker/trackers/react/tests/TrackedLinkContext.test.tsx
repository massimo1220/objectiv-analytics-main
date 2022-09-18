/*
 * Copyright 2022 Objectiv B.V.
 */

import { LogTransport, MockConsoleImplementation } from '@objectiv/testing-tools';
import { LocationContextName } from '@objectiv/tracker-core';
import { fireEvent, getByText, render, waitFor } from '@testing-library/react';
import React, { createRef } from 'react';
import { ObjectivProvider, ReactTracker, TrackedDiv, TrackedLinkContext, TrackedRootLocationContext } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('TrackedLinkContext', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    jest.spyOn(console, 'error').mockImplementation(jest.fn);
    globalThis.objectiv.TrackerRepository.trackersMap.clear();
    globalThis.objectiv.TrackerRepository.defaultTracker = undefined;
  });

  afterEach(() => {
    jest.resetAllMocks();
    jest.useRealTimers();
  });

  it('should wrap the given Component in a LinkContext', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <TrackedLinkContext href={'/some-url-1'} objectiv={{ Component: 'a', id: 'link-id-1' }}>
          Trigger Event 1
        </TrackedLinkContext>
        <TrackedLinkContext objectiv={{ Component: 'a', id: 'link-id-2', href: '/some-url-2' }}>
          Trigger Event 2
        </TrackedLinkContext>
      </ObjectivProvider>
    );

    fireEvent.click(getByText(container, /trigger event 1/i));
    fireEvent.click(getByText(container, /trigger event 2/i));

    expect(logTransport.handle).toHaveBeenCalledTimes(3);
    expect(logTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'ApplicationLoadedEvent',
      })
    );
    expect(logTransport.handle).toHaveBeenNthCalledWith(
      2,
      expect.objectContaining({
        _type: 'PressEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.LinkContext,
            id: 'link-id-1',
            href: '/some-url-1',
          }),
        ]),
      })
    );
    expect(logTransport.handle).toHaveBeenNthCalledWith(
      3,
      expect.objectContaining({
        _type: 'PressEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.LinkContext,
            id: 'link-id-2',
            href: '/some-url-2',
          }),
        ]),
      })
    );
  });

  it('should allow disabling id normalization', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <TrackedLinkContext href={'/some-url'} objectiv={{ Component: 'a', id: 'Link Id 1' }}>
          Trigger Event 1
        </TrackedLinkContext>
        <TrackedLinkContext href={'/some-url'} objectiv={{ Component: 'a', id: 'Link Id 2', normalizeId: false }}>
          Trigger Event 2
        </TrackedLinkContext>
      </ObjectivProvider>
    );

    fireEvent.click(getByText(container, /trigger event 1/i));
    fireEvent.click(getByText(container, /trigger event 2/i));

    expect(logTransport.handle).toHaveBeenCalledTimes(3);
    expect(logTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'ApplicationLoadedEvent',
      })
    );
    expect(logTransport.handle).toHaveBeenNthCalledWith(
      2,
      expect.objectContaining({
        _type: 'PressEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.LinkContext,
            id: 'link-id-1',
          }),
        ]),
      })
    );
    expect(logTransport.handle).toHaveBeenNthCalledWith(
      3,
      expect.objectContaining({
        _type: 'PressEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.LinkContext,
            id: 'Link Id 2',
          }),
        ]),
      })
    );
  });

  it('should console.error if an id cannot be automatically generated', () => {
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new LogTransport() });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedRootLocationContext objectiv={{ Component: 'div', id: 'root' }}>
          <TrackedDiv objectiv={{ id: 'content' }}>
            <TrackedLinkContext href={'/some-url'} objectiv={{ Component: 'a' }}>
              {/* nothing to see here */}
            </TrackedLinkContext>
          </TrackedDiv>
        </TrackedRootLocationContext>
      </ObjectivProvider>
    );

    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv｣ Could not generate a valid id for LinkContext @ RootLocation:root / Content:content. Please provide either the `title` or the `objectiv.id` property manually.'
    );
  });

  it('should console.error if an href cannot be retrieved', () => {
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new LogTransport() });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedRootLocationContext objectiv={{ Component: 'div', id: 'root' }}>
          <TrackedDiv objectiv={{ id: 'content' }}>
            <TrackedLinkContext objectiv={{ Component: 'a' }}>Press Me!</TrackedLinkContext>
          </TrackedDiv>
        </TrackedRootLocationContext>
      </ObjectivProvider>
    );

    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv｣ Could not generate a valid href for LinkContext @ RootLocation:root / Content:content. Please provide the `objectiv.href` property manually.'
    );
  });

  it('should allow forwarding refs', () => {
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new LogTransport() });
    const ref = createRef<HTMLDivElement>();

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedLinkContext href={'/some-url'} ref={ref} objectiv={{ Component: 'a' }}>
          Press me!
        </TrackedLinkContext>
      </ObjectivProvider>
    );

    expect(ref.current).toMatchInlineSnapshot(`
      <a
        href="/some-url"
      >
        Press me!
      </a>
    `);
  });

  it('should execute the given onClick as well', async () => {
    const clickSpy = jest.fn();
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new LogTransport() });

    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <TrackedLinkContext href={'/some-url'} onClick={clickSpy} objectiv={{ Component: 'a', id: 'link-id' }}>
          Press me
        </TrackedLinkContext>
      </ObjectivProvider>
    );

    fireEvent.click(getByText(container, /press me/i));

    await waitFor(() => expect(clickSpy).toHaveBeenCalledTimes(1));
  });

  it('should not wait until tracked', async () => {
    jest.useFakeTimers();
    const clickSpy = jest.fn();
    const logTransport = new LogTransport();
    const handleMock = jest.fn(async () => new Promise((resolve) => setTimeout(resolve, 10000)));
    jest.spyOn(logTransport, 'handle').mockImplementation(handleMock);
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <TrackedLinkContext
          href={'/some-url'}
          waitUntilTracked={false}
          onClick={clickSpy}
          objectiv={{ Component: 'a', waitUntilTracked: false }}
        >
          Press me
        </TrackedLinkContext>
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.click(getByText(container, /press me/i));

    await waitFor(() => expect(clickSpy).toHaveBeenCalledTimes(1));

    expect(handleMock).not.toHaveBeenCalled();
  });

  it('should wait until tracked', async () => {
    jest.useFakeTimers();
    const clickSpy = jest.fn();
    const logTransport = new LogTransport();
    jest
      .spyOn(logTransport, 'handle')
      .mockImplementation(async () => new Promise((resolve) => setTimeout(resolve, 100)));
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <TrackedLinkContext href={'/some-url'} onClick={clickSpy} objectiv={{ Component: 'a', waitUntilTracked: true }}>
          Press me
        </TrackedLinkContext>
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.click(getByText(container, /press me/i));

    await waitFor(() => expect(clickSpy).toHaveBeenCalledTimes(1));

    expect(logTransport.handle).toHaveBeenCalledTimes(1);
    expect(logTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'PressEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.LinkContext,
            id: 'press-me',
          }),
        ]),
      })
    );
  });
});
