/*
 * Copyright 2022 Objectiv B.V.
 */

import { MockConsoleImplementation, LogTransport } from '@objectiv/testing-tools';
import { LocationContextName } from '@objectiv/tracker-core';
import { fireEvent, getByText, render } from '@testing-library/react';
import React from 'react';
import {
  ObjectivProvider,
  ReactTracker,
  TrackedDiv,
  TrackedRootLocationContext,
  TrackedSection,
  usePressEventTracker,
} from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('TrackedSection', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    globalThis.objectiv.TrackerRepository.trackersMap.clear();
    globalThis.objectiv.TrackerRepository.defaultTracker = undefined;
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given Component in a ContentContext', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    const TrackedButton = () => {
      const trackPressEvent = usePressEventTracker();
      return <div onClick={() => trackPressEvent()}>Trigger Event</div>;
    };

    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <TrackedSection objectiv={{ id: 'section-id' }}>
          <TrackedButton />
        </TrackedSection>
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.click(getByText(container, /trigger event/i));

    expect(logTransport.handle).toHaveBeenCalledTimes(1);
    expect(logTransport.handle).toHaveBeenCalledWith(
      expect.objectContaining({
        _type: 'PressEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.ContentContext,
            id: 'section-id',
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
        <TrackedSection objectiv={{ id: 'Section 1' }}>
          <TrackedButton>Trigger Event 1</TrackedButton>
        </TrackedSection>
        <TrackedSection objectiv={{ id: 'Section 2', normalizeId: false }}>
          <TrackedButton>Trigger Event 2</TrackedButton>
        </TrackedSection>
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.click(getByText(container, /trigger event 1/i));
    fireEvent.click(getByText(container, /trigger event 2/i));

    expect(logTransport.handle).toHaveBeenCalledTimes(2);
    expect(logTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'PressEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.ContentContext,
            id: 'section-1',
          }),
        ]),
      })
    );
    expect(logTransport.handle).toHaveBeenNthCalledWith(
      2,
      expect.objectContaining({
        _type: 'PressEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.ContentContext,
            id: 'Section 2',
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
            <TrackedSection id={'☹️'} />
            <TrackedSection />
          </TrackedDiv>
        </TrackedRootLocationContext>
      </ObjectivProvider>
    );

    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(2);
    expect(MockConsoleImplementation.error).toHaveBeenNthCalledWith(
      1,
      '｢objectiv｣ Could not generate a valid id for ContentContext @ RootLocation:root / Content:content. Please provide the `objectiv.id` property.'
    );
    expect(MockConsoleImplementation.error).toHaveBeenNthCalledWith(
      2,
      '｢objectiv｣ Could not generate a valid id for ContentContext @ RootLocation:root / Content:content. Please provide the `objectiv.id` property.'
    );
  });
});
