/*
 * Copyright 2022 Objectiv B.V.
 */

import { LogTransport, MockConsoleImplementation } from '@objectiv/testing-tools';
import { LocationContextName } from '@objectiv/tracker-core';
import { fireEvent, getByText, render, waitFor } from '@testing-library/react';
import React, { createRef } from 'react';
import {
  ObjectivProvider,
  ReactTracker,
  TrackedDiv,
  TrackedPressableContext,
  TrackedRootLocationContext,
} from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('TrackedPressableContext', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    globalThis.objectiv.TrackerRepository.trackersMap.clear();
    globalThis.objectiv.TrackerRepository.defaultTracker = undefined;
  });

  afterEach(() => {
    jest.resetAllMocks();
    jest.useRealTimers();
  });

  it('should wrap the given Component in a PressableContext', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <TrackedPressableContext objectiv={{ Component: 'button', id: 'pressable-id' }}>
          Trigger Event
        </TrackedPressableContext>
      </ObjectivProvider>
    );

    fireEvent.click(getByText(container, /trigger event/i));

    expect(logTransport.handle).toHaveBeenCalledTimes(2);
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
            _type: LocationContextName.PressableContext,
            id: 'pressable-id',
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
        <TrackedPressableContext objectiv={{ Component: 'button', id: 'Pressable id 1' }}>
          Trigger Event 1
        </TrackedPressableContext>
        <TrackedPressableContext objectiv={{ Component: 'button', id: 'Pressable id 2', normalizeId: false }}>
          Trigger Event 2
        </TrackedPressableContext>
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
            _type: LocationContextName.PressableContext,
            id: 'pressable-id-1',
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
            _type: LocationContextName.PressableContext,
            id: 'Pressable id 2',
          }),
        ]),
      })
    );
  });

  it('should console.error if an id cannot be automatically generated', () => {
    jest.spyOn(console, 'error').mockImplementation(() => {});
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new LogTransport() });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedRootLocationContext objectiv={{ Component: 'div', id: 'root' }}>
          <TrackedDiv objectiv={{ id: 'content' }}>
            <TrackedPressableContext objectiv={{ Component: 'button' }}>
              {/* nothing to see here */}
            </TrackedPressableContext>
          </TrackedDiv>
        </TrackedRootLocationContext>
      </ObjectivProvider>
    );

    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv｣ Could not generate a valid id for PressableContext @ RootLocation:root / Content:content. Please provide either the `title` or the `objectiv.id` property manually.'
    );
  });

  it('should allow forwarding refs', () => {
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new LogTransport() });
    const ref = createRef<HTMLDivElement>();

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedPressableContext ref={ref} objectiv={{ Component: 'a' }}>
          Press me!
        </TrackedPressableContext>
      </ObjectivProvider>
    );

    expect(ref.current).toMatchInlineSnapshot(`
      <a>
        Press me!
      </a>
    `);
  });

  it('should execute the given onClick as well', async () => {
    const clickSpy = jest.fn();
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new LogTransport() });

    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <TrackedPressableContext onClick={clickSpy} objectiv={{ Component: 'button', id: 'pressable-id' }}>
          Press me
        </TrackedPressableContext>
      </ObjectivProvider>
    );

    fireEvent.click(getByText(container, /press me/i));

    await waitFor(() => expect(clickSpy).toHaveBeenCalledTimes(1));
  });
});
