/*
 * Copyright 2022 Objectiv B.V.
 */

import { LogTransport, MockConsoleImplementation } from '@objectiv/testing-tools';
import { GlobalContextName, LocationContextName } from '@objectiv/tracker-core';
import { fireEvent, render, screen } from '@testing-library/react';
import React, { createRef } from 'react';
import { ObjectivProvider, ReactTracker, TrackedDiv, TrackedInputRadio, TrackedRootLocationContext } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('TrackedInputRadio', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    globalThis.objectiv.TrackerRepository.trackersMap.clear();
    globalThis.objectiv.TrackerRepository.defaultTracker = undefined;
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should not allow changing the type attribute', () => {
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new LogTransport() });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputRadio value={'value-1'} />
        <TrackedInputRadio objectiv={{ id: 'value-1' }} />
        <TrackedInputRadio type={'radio'} value={'value-2'} />
        <TrackedInputRadio type={'text'} id={'input-id'} value={'value-3'} />
      </ObjectivProvider>
    );

    expect(MockConsoleImplementation.warn).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.warn).toHaveBeenCalledWith(
      "｢objectiv｣ TrackedInputRadio type attribute can only be set to 'radio'."
    );
  });

  it('should wrap the given Component in an InputContext', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputRadio id={'input-id'} data-testid={'test-radio'} value={'value'} />
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.click(screen.getByTestId('test-radio'), { target: { value: 'value1' } });

    expect(logTransport.handle).toHaveBeenCalledTimes(1);
    expect(logTransport.handle).toHaveBeenCalledWith(
      expect.objectContaining({
        _type: 'InputChangeEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.InputContext,
            id: 'input-id',
          }),
        ]),
        global_contexts: expect.not.arrayContaining([
          expect.objectContaining({
            _type: GlobalContextName.InputValueContext,
          }),
        ]),
      })
    );
  });

  it('should allow tracking values as InputValueContexts', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputRadio data-testid={'test-radio-1'} name={'name'} objectiv={{ trackValue: true }} />
        <TrackedInputRadio data-testid={'test-radio-2'} value={'value'} objectiv={{ trackValue: true }} />
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.click(screen.getByTestId('test-radio-1'));
    fireEvent.click(screen.getByTestId('test-radio-2'));

    expect(logTransport.handle).toHaveBeenCalledTimes(2);
    expect(logTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'InputChangeEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.InputContext,
            id: 'name',
          }),
        ]),
        global_contexts: expect.arrayContaining([
          expect.objectContaining({
            _type: GlobalContextName.ApplicationContext,
          }),
          expect.objectContaining({
            _type: GlobalContextName.PathContext,
          }),
          expect.objectContaining({
            _type: GlobalContextName.HttpContext,
          }),
          expect.objectContaining({
            _type: GlobalContextName.InputValueContext,
            id: 'name',
            value: '1',
          }),
        ]),
      })
    );
    expect(logTransport.handle).toHaveBeenNthCalledWith(
      2,
      expect.objectContaining({
        _type: 'InputChangeEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.InputContext,
            id: 'value',
          }),
        ]),
        global_contexts: expect.arrayContaining([
          expect.objectContaining({
            _type: GlobalContextName.ApplicationContext,
          }),
          expect.objectContaining({
            _type: GlobalContextName.PathContext,
          }),
          expect.objectContaining({
            _type: GlobalContextName.HttpContext,
          }),
          expect.objectContaining({
            _type: GlobalContextName.InputValueContext,
            id: 'value',
            value: '1',
          }),
        ]),
      })
    );
  });

  it('should allow tracking on onBlur', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputRadio
          id={'input-id'}
          data-testid={'test-radio'}
          value={'value'}
          objectiv={{ eventHandler: 'onBlur' }}
        />
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.blur(screen.getByTestId('test-radio'));

    expect(logTransport.handle).toHaveBeenCalledTimes(1);
    expect(logTransport.handle).toHaveBeenCalledWith(
      expect.objectContaining({
        _type: 'InputChangeEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.InputContext,
            id: 'input-id',
          }),
        ]),
      })
    );
  });

  it('should allow tracking on onChange', async () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    const onChangeSpy = jest.fn();

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputRadio
          id={'input-id-1'}
          data-testid={'test-radio-1'}
          value={'value-1'}
          name={'radios'}
          onChange={onChangeSpy}
          objectiv={{ eventHandler: 'onChange' }}
        />
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    // NOTE: we trigger click here instead of change, because the latter doesn't actually work
    fireEvent.click(screen.getByTestId('test-radio-1'));

    // This spy actually confirms that onChange triggered
    expect(onChangeSpy).toHaveBeenCalledTimes(1);

    expect(logTransport.handle).toHaveBeenCalledTimes(1);
    expect(logTransport.handle).toHaveBeenCalledWith(
      expect.objectContaining({
        _type: 'InputChangeEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.InputContext,
            id: 'input-id-1',
          }),
        ]),
      })
    );
  });

  it('should allow tracking stateful mode, e.g. blur events with no changes', async () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputRadio
          id={'input-id-1'}
          data-testid={'test-radio-1'}
          value={'value-1'}
          objectiv={{ eventHandler: 'onBlur', stateless: false }}
        />
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    // NOTE: we trigger click here instead of change, because the latter doesn't actually work
    fireEvent.blur(screen.getByTestId('test-radio-1'));
    fireEvent.blur(screen.getByTestId('test-radio-1'));
    fireEvent.blur(screen.getByTestId('test-radio-1'));

    expect(logTransport.handle).toHaveBeenCalledTimes(1);
    expect(logTransport.handle).toHaveBeenCalledWith(expect.objectContaining({ _type: 'InputChangeEvent' }));
  });

  it('should allow disabling id normalization', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputRadio id={'Input id 1'} data-testid={'test-radio-1'} value={'text'} />
        <TrackedInputRadio
          id={'Input id 2'}
          data-testid={'test-radio-2'}
          value={'text'}
          objectiv={{ normalizeId: false }}
        />
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.click(screen.getByTestId('test-radio-1'));
    fireEvent.click(screen.getByTestId('test-radio-2'));

    expect(logTransport.handle).toHaveBeenCalledTimes(2);
    expect(logTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'InputChangeEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.InputContext,
            id: 'input-id-1',
          }),
        ]),
      })
    );
    expect(logTransport.handle).toHaveBeenNthCalledWith(
      2,
      expect.objectContaining({
        _type: 'InputChangeEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.InputContext,
            id: 'Input id 2',
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
          <TrackedDiv id={'content'}>
            <TrackedInputRadio id={'☹️'} />
          </TrackedDiv>
        </TrackedRootLocationContext>
      </ObjectivProvider>
    );

    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv｣ Could not generate a valid id for InputContext:radio @ RootLocation:root / Content:content. Please provide the `objectiv.id` property.'
    );
  });

  it('should console.error if an id cannot be automatically generated from value', () => {
    jest.spyOn(console, 'error').mockImplementation(() => {});
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new LogTransport() });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedRootLocationContext objectiv={{ Component: 'div', id: 'root' }}>
          <TrackedDiv id={'content'}>
            <TrackedInputRadio value={''} />
          </TrackedDiv>
        </TrackedRootLocationContext>
      </ObjectivProvider>
    );

    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv｣ Could not generate a valid id for InputContext:radio @ RootLocation:root / Content:content. Please provide the `objectiv.id` property.'
    );
  });

  it('should allow forwarding refs', () => {
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new LogTransport() });
    const ref = createRef<HTMLInputElement>();

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputRadio value={'test 1'} ref={ref} />
      </ObjectivProvider>
    );

    expect(ref.current).toMatchInlineSnapshot(`
      <input
        type="radio"
        value="test 1"
      />
    `);
  });

  it('should allow tracking onBlur instead of onChange', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    const onBlurSpy = jest.fn();

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputRadio
          value={'some-value'}
          data-testid={'test-input'}
          onBlur={onBlurSpy}
          objectiv={{ eventHandler: 'onBlur' }}
        />
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.blur(screen.getByTestId('test-input'), { target: { value: 'some new text' } });

    expect(logTransport.handle).toHaveBeenCalledWith(
      expect.objectContaining({
        _type: 'InputChangeEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.InputContext,
            id: 'some-value',
          }),
        ]),
      })
    );
    expect(onBlurSpy).toHaveBeenCalled();
  });

  it('should allow tracking onClick instead of onChange', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    const onClickSpy = jest.fn();

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputRadio
          value={'some-value'}
          data-testid={'test-input'}
          onClick={onClickSpy}
          objectiv={{ eventHandler: 'onChange' }}
        />
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.click(screen.getByTestId('test-input'), { target: { value: 'some new text' } });

    expect(logTransport.handle).toHaveBeenCalledWith(
      expect.objectContaining({
        _type: 'InputChangeEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.InputContext,
            id: 'some-value',
          }),
        ]),
      })
    );
    expect(onClickSpy).toHaveBeenCalled();
  });

  it('should track as many times as interacted, regardless of its value being the same', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputRadio
          id={'input-id'}
          data-testid={'test-radio'}
          value={'value'}
          objectiv={{ eventHandler: 'onClick', trackValue: true }}
        />
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.click(screen.getByTestId('test-radio'));
    fireEvent.click(screen.getByTestId('test-radio'));
    fireEvent.click(screen.getByTestId('test-radio'));

    expect(logTransport.handle).toHaveBeenCalledTimes(3);
    const expectedEventPayload = {
      _type: 'InputChangeEvent',
      location_stack: expect.arrayContaining([
        expect.objectContaining({
          _type: LocationContextName.InputContext,
          id: 'input-id',
        }),
      ]),
      global_contexts: expect.arrayContaining([
        expect.objectContaining({
          _type: GlobalContextName.InputValueContext,
          id: 'input-id',
          value: expect.stringMatching('0|1'),
        }),
      ]),
    };
    expect(logTransport.handle).toHaveBeenNthCalledWith(1, expect.objectContaining(expectedEventPayload));
    expect(logTransport.handle).toHaveBeenNthCalledWith(2, expect.objectContaining(expectedEventPayload));
    expect(logTransport.handle).toHaveBeenNthCalledWith(3, expect.objectContaining(expectedEventPayload));
  });
});
