/*
 * Copyright 2022 Objectiv B.V.
 */

import { LogTransport, MockConsoleImplementation } from '@objectiv/testing-tools';
import { LocationContextName } from '@objectiv/tracker-core';
import { fireEvent, getByText, render } from '@testing-library/react';
import React, { createRef } from 'react';
import { ObjectivProvider, ReactTracker, TrackedRootLocationContext, usePressEventTracker } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('TrackedRootLocationContext', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    globalThis.objectiv.TrackerRepository.trackersMap.clear();
    globalThis.objectiv.TrackerRepository.defaultTracker = undefined;
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given Component in a RootLocationContext', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    const TrackedButton = ({ text = 'Trigger Event' }: { text?: string }) => {
      const trackPressEvent = usePressEventTracker();
      return <div onClick={() => trackPressEvent()}>{text}</div>;
    };

    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <TrackedRootLocationContext objectiv={{ Component: 'div', id: 'root-id-1' }}>
          <TrackedButton text={'Trigger Event 1'} />
        </TrackedRootLocationContext>
        <TrackedRootLocationContext id={'root-id-2'} objectiv={{ Component: 'div' }}>
          <TrackedButton text={'Trigger Event 2'} />
        </TrackedRootLocationContext>
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
            _type: LocationContextName.RootLocationContext,
            id: 'root-id-1',
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
            _type: LocationContextName.RootLocationContext,
            id: 'root-id-2',
          }),
        ]),
      })
    );
  });

  it('should allow disabling id normalization', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    const TrackedButton = ({ children }: { children: React.ReactNode }) => {
      const trackPressEvent = usePressEventTracker();
      return <div onClick={() => trackPressEvent()}>{children}</div>;
    };

    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <TrackedRootLocationContext objectiv={{ Component: 'div', id: 'Root id 1' }}>
          <TrackedButton>Trigger Event 1</TrackedButton>
        </TrackedRootLocationContext>
        <TrackedRootLocationContext objectiv={{ Component: 'div', id: 'Root id 2', normalizeId: false }}>
          <TrackedButton>Trigger Event 2</TrackedButton>
        </TrackedRootLocationContext>
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
            _type: LocationContextName.RootLocationContext,
            id: 'root-id-1',
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
            _type: LocationContextName.RootLocationContext,
            id: 'Root id 2',
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
        <TrackedRootLocationContext objectiv={{ Component: 'div', id: '☹️' }} />
      </ObjectivProvider>
    );

    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv｣ Could not generate a valid id for RootLocationContext. Please provide the `objectiv.id` property.'
    );
  });

  it('should allow forwarding refs', () => {
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new LogTransport() });
    const ref = createRef<HTMLDivElement>();

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedRootLocationContext ref={ref} objectiv={{ Component: 'div', id: 'root-id' }}>
          test
        </TrackedRootLocationContext>
      </ObjectivProvider>
    );

    expect(ref.current).toMatchInlineSnapshot(`
      <div>
        test
      </div>
    `);
  });
});
