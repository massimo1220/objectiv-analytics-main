/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { LogTransport, MockConsoleImplementation } from '@objectiv/testing-tools';
import { GlobalContextName, LocationContextName } from '@objectiv/tracker-core';
import { fireEvent, render, screen } from '@testing-library/react';
import React, { createRef } from 'react';
import { ObjectivProvider, ReactTracker, TrackedDiv, TrackedInputContext, TrackedRootLocationContext } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv.devTools?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('TrackedInputContext', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    globalThis.objectiv.TrackerRepository.trackersMap.clear();
    globalThis.objectiv.TrackerRepository.defaultTracker = undefined;
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given Component in an InputContext and not trigger InputChangeEvent on mount', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputContext
          data-testid={'test-input'}
          value={'test'}
          objectiv={{ Component: 'input', id: 'input-id' }}
        />
      </ObjectivProvider>
    );

    fireEvent.blur(screen.getByTestId('test-input'));

    expect(logTransport.handle).toHaveBeenCalledTimes(1);
    expect(logTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'ApplicationLoadedEvent',
      })
    );
  });

  it('should allow disabling id normalization', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputContext
          type={'text'}
          data-testid={'test-input-1'}
          objectiv={{ Component: 'input', id: 'Input id 1' }}
        />
        <TrackedInputContext
          type={'text'}
          data-testid={'test-input-2'}
          objectiv={{ Component: 'input', id: 'Input id 2', normalizeId: false }}
        />
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.blur(screen.getByTestId('test-input-1'), { target: { value: 'some new text 1' } });
    fireEvent.blur(screen.getByTestId('test-input-2'), { target: { value: 'some new text 2' } });

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

  it('should allow tracking select elements', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputContext
          data-testid={'test-select'}
          objectiv={{ Component: 'select', id: 'test-select', eventHandler: 'onChange', trackValue: true }}
        >
          <option data-testid={'test-option-1'} value={'option-1'}>
            option 1
          </option>
          <option data-testid={'test-option-2'} value={'option-2'}>
            option 2
          </option>
          <option data-testid={'test-option-3'} value={'option-3'}>
            option 3
          </option>
        </TrackedInputContext>
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    fireEvent.change(screen.getByTestId('test-select'), { target: { value: 'option-2' } });

    expect(logTransport.handle).toHaveBeenCalledTimes(1);
    expect(logTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'InputChangeEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.InputContext,
            id: 'test-select',
          }),
        ]),
        global_contexts: expect.arrayContaining([
          expect.objectContaining({
            _type: GlobalContextName.InputValueContext,
            id: 'test-select',
            value: 'option-2',
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
            <TrackedInputContext type={'text'} objectiv={{ Component: 'input', id: '☹️' }} />
          </TrackedDiv>
        </TrackedRootLocationContext>
      </ObjectivProvider>
    );

    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv｣ Could not generate a valid id for InputContext:text @ RootLocation:root / Content:content. Please provide the `objectiv.id` property.'
    );
  });

  it('should not track an InputChangeEvent when value did not change from the previous InputChangeEvent', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputContext
          type={'text'}
          defaultValue={'some text'}
          data-testid={'test-input'}
          objectiv={{ Component: 'input', id: 'input-id' }}
        />
      </ObjectivProvider>
    );

    fireEvent.blur(screen.getByTestId('test-input'), { target: { value: 'some text' } });
    fireEvent.blur(screen.getByTestId('test-input'), { target: { value: 'some text' } });
    fireEvent.blur(screen.getByTestId('test-input'), { target: { value: 'some text' } });

    expect(logTransport.handle).not.toHaveBeenCalledWith(
      expect.objectContaining({
        _type: 'InputChangeEvent',
      })
    );
  });

  it('should track every interaction as InputChangeEvent regardless of value changes when stateless is set', () => {
    const logTransport = new LogTransport();
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputContext
          type={'text'}
          defaultValue={'some text'}
          data-testid={'test-input-1'}
          objectiv={{ Component: 'input', id: 'input-id-1', stateless: true }}
        />
        <TrackedInputContext
          type={'radio'}
          checked={true}
          data-testid={'test-input-2'}
          objectiv={{ Component: 'input', id: 'input-id-2', stateless: true, eventHandler: 'onClick' }}
          onClick={jest.fn}
        />
        <TrackedInputContext
          data-testid={'test-input-3'}
          objectiv={{ Component: 'select', id: 'input-id-3', stateless: true, eventHandler: 'onClick' }}
        />
        <TrackedInputContext
          data-testid={'test-input-4'}
          multiple
          objectiv={{ Component: 'select', id: 'input-id-4', stateless: true, eventHandler: 'onClick' }}
        />
        <TrackedInputContext
          type={'checkbox'}
          checked={true}
          data-testid={'test-input-5'}
          objectiv={{ Component: 'input', id: 'input-id-5', stateless: true, eventHandler: 'onClick' }}
        />
      </ObjectivProvider>
    );

    jest.spyOn(logTransport, 'handle');

    fireEvent.blur(screen.getByTestId('test-input-1'), { target: { value: 'some text' } });
    fireEvent.blur(screen.getByTestId('test-input-1'), { target: { value: 'some text' } });
    fireEvent.blur(screen.getByTestId('test-input-1'), { target: { value: 'some text' } });

    expect(logTransport.handle).toHaveBeenCalledTimes(3);
    expect(logTransport.handle).toHaveBeenNthCalledWith(1, expect.objectContaining({ _type: 'InputChangeEvent' }));
    expect(logTransport.handle).toHaveBeenNthCalledWith(2, expect.objectContaining({ _type: 'InputChangeEvent' }));
    expect(logTransport.handle).toHaveBeenNthCalledWith(3, expect.objectContaining({ _type: 'InputChangeEvent' }));

    jest.resetAllMocks();

    fireEvent.click(screen.getByTestId('test-input-2'), { target: { checked: true } });
    fireEvent.click(screen.getByTestId('test-input-2'), { target: { checked: true } });
    fireEvent.click(screen.getByTestId('test-input-2'), { target: { checked: true } });

    expect(logTransport.handle).toHaveBeenCalledTimes(3);
    expect(logTransport.handle).toHaveBeenNthCalledWith(1, expect.objectContaining({ _type: 'InputChangeEvent' }));
    expect(logTransport.handle).toHaveBeenNthCalledWith(2, expect.objectContaining({ _type: 'InputChangeEvent' }));
    expect(logTransport.handle).toHaveBeenNthCalledWith(3, expect.objectContaining({ _type: 'InputChangeEvent' }));

    jest.resetAllMocks();

    fireEvent.click(screen.getByTestId('test-input-3'), { target: { value: 'option' } });
    fireEvent.click(screen.getByTestId('test-input-3'), { target: { value: 'option' } });
    fireEvent.click(screen.getByTestId('test-input-3'), { target: { value: 'option' } });

    expect(logTransport.handle).toHaveBeenCalledTimes(3);
    expect(logTransport.handle).toHaveBeenNthCalledWith(1, expect.objectContaining({ _type: 'InputChangeEvent' }));
    expect(logTransport.handle).toHaveBeenNthCalledWith(2, expect.objectContaining({ _type: 'InputChangeEvent' }));
    expect(logTransport.handle).toHaveBeenNthCalledWith(3, expect.objectContaining({ _type: 'InputChangeEvent' }));

    jest.resetAllMocks();

    fireEvent.click(screen.getByTestId('test-input-4'), { target: { value: 'option' } });
    fireEvent.click(screen.getByTestId('test-input-4'), { target: { value: 'option' } });
    fireEvent.click(screen.getByTestId('test-input-4'), { target: { value: 'option' } });

    expect(logTransport.handle).toHaveBeenCalledTimes(3);
    expect(logTransport.handle).toHaveBeenNthCalledWith(1, expect.objectContaining({ _type: 'InputChangeEvent' }));
    expect(logTransport.handle).toHaveBeenNthCalledWith(2, expect.objectContaining({ _type: 'InputChangeEvent' }));
    expect(logTransport.handle).toHaveBeenNthCalledWith(3, expect.objectContaining({ _type: 'InputChangeEvent' }));

    jest.resetAllMocks();

    fireEvent.click(screen.getByTestId('test-input-5'), { target: { checked: true } });
    fireEvent.click(screen.getByTestId('test-input-5'), { target: { checked: true } });
    fireEvent.click(screen.getByTestId('test-input-5'), { target: { checked: true } });

    expect(logTransport.handle).toHaveBeenCalledTimes(3);
    expect(logTransport.handle).toHaveBeenNthCalledWith(1, expect.objectContaining({ _type: 'InputChangeEvent' }));
    expect(logTransport.handle).toHaveBeenNthCalledWith(2, expect.objectContaining({ _type: 'InputChangeEvent' }));
    expect(logTransport.handle).toHaveBeenNthCalledWith(3, expect.objectContaining({ _type: 'InputChangeEvent' }));
  });

  it('should track the also the checked attribute for checkboxes', () => {
    const logTransport = new LogTransport();
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputContext
          type={'checkbox'}
          value={'123'}
          data-testid={'test-checkbox'}
          objectiv={{
            Component: 'input',
            id: 'checkbox-id',
            stateless: true,
            trackValue: true,
            eventHandler: 'onClick',
          }}
        />
      </ObjectivProvider>
    );

    jest.spyOn(logTransport, 'handle');

    fireEvent.click(screen.getByTestId('test-checkbox'), { target: { checked: true } });
    fireEvent.click(screen.getByTestId('test-checkbox'), { target: { checked: false } });
    fireEvent.click(screen.getByTestId('test-checkbox'), { target: { checked: true } });

    expect(logTransport.handle).toHaveBeenCalledTimes(3);
    expect(logTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'InputChangeEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.InputContext,
            id: 'checkbox-id',
          }),
        ]),
        global_contexts: expect.not.arrayContaining([
          expect.objectContaining({
            _type: GlobalContextName.InputValueContext,
            id: 'checkbox-id',
            value: '123',
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
            id: 'checkbox-id',
          }),
        ]),
        global_contexts: expect.not.arrayContaining([
          expect.objectContaining({
            _type: GlobalContextName.InputValueContext,
            id: 'checkbox-id',
            value: '123',
          }),
        ]),
      })
    );
    expect(logTransport.handle).toHaveBeenNthCalledWith(
      3,
      expect.objectContaining({
        _type: 'InputChangeEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.InputContext,
            id: 'checkbox-id',
          }),
        ]),
        global_contexts: expect.not.arrayContaining([
          expect.objectContaining({
            _type: GlobalContextName.InputValueContext,
            id: 'checkbox-id',
            value: '123',
          }),
        ]),
      })
    );
  });

  it('should track an InputChangeEvent when value changed from the previous InputChangeEvent', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputContext
          type={'text'}
          defaultValue={'some text'}
          data-testid={'test-input'}
          objectiv={{ Component: 'input', id: 'input-id' }}
        />
      </ObjectivProvider>
    );

    fireEvent.blur(screen.getByTestId('test-input'), { target: { value: 'some new text' } });

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
            id: 'input-id',
            value: 'some new text',
          }),
        ]),
      })
    );
  });

  it('should allow tracking InputValueContext when an InputChangeEvent triggers', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputContext
          type={'text'}
          defaultValue={'some text'}
          data-testid={'test-input'}
          objectiv={{ Component: 'input', id: 'input-id', trackValue: true }}
        />
      </ObjectivProvider>
    );

    fireEvent.blur(screen.getByTestId('test-input'), { target: { value: 'some new text' } });

    expect(logTransport.handle).toHaveBeenCalledWith(
      expect.objectContaining({
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
            value: 'some new text',
          }),
        ]),
      })
    );
  });

  it('should allow tracking onChange instead of onBlur', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    const onBlurSpy = jest.fn();
    const onChangeSpy = jest.fn();
    const onClickSpy = jest.fn();

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputContext
          type={'text'}
          defaultValue={'some text'}
          data-testid={'test-input'}
          onBlur={onBlurSpy}
          onChange={onChangeSpy}
          onClick={onClickSpy}
          objectiv={{ Component: 'input', id: 'input-id', trackValue: true, eventHandler: 'onChange' }}
        />
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    // Should ignore blur events, because we configured onChange as event handler above
    fireEvent.blur(screen.getByTestId('test-input'), { target: { value: 'some new text' } });
    expect(logTransport.handle).not.toHaveBeenCalled();
    // But it should have still triggered the given onBlur
    expect(onBlurSpy).toHaveBeenCalledTimes(1);

    jest.resetAllMocks();

    // Should ignore click events, because we configured onChange as event handler above
    fireEvent.click(screen.getByTestId('test-input'));
    expect(logTransport.handle).not.toHaveBeenCalled();
    // But it should have still triggered the given onClick
    expect(onClickSpy).toHaveBeenCalledTimes(1);

    jest.resetAllMocks();

    fireEvent.change(screen.getByTestId('test-input'), { target: { value: 'some new text' } });

    expect(logTransport.handle).toHaveBeenCalledWith(
      expect.objectContaining({
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
            value: 'some new text',
          }),
        ]),
      })
    );
    expect(onBlurSpy).not.toHaveBeenCalled();
    expect(onChangeSpy).toHaveBeenCalledTimes(1);
  });

  it('should allow tracking onClick instead of onBlur', () => {
    const logTransport = new LogTransport();
    jest.spyOn(logTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: logTransport });

    const onBlurSpy = jest.fn();
    const onChangeSpy = jest.fn();
    const onClickSpy = jest.fn();

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputContext
          type={'text'}
          defaultValue={'some text'}
          data-testid={'test-input'}
          onBlur={onBlurSpy}
          onChange={onChangeSpy}
          onClick={onClickSpy}
          objectiv={{ Component: 'input', id: 'input-id', trackValue: true, eventHandler: 'onClick' }}
        />
      </ObjectivProvider>
    );

    jest.resetAllMocks();

    // Should ignore blur events, because we configured onChange as event handler above
    fireEvent.blur(screen.getByTestId('test-input'), { target: { value: 'some new text' } });
    expect(logTransport.handle).not.toHaveBeenCalled();
    // But it should have still triggered the given onBlur
    expect(onBlurSpy).toHaveBeenCalledTimes(1);

    jest.resetAllMocks();

    // Should ignore change events, because we configured onChange as event handler above
    fireEvent.change(screen.getByTestId('test-input'), { target: { value: 'some new text' } });
    expect(logTransport.handle).not.toHaveBeenCalled();
    // But it should have still triggered the given onChange
    expect(onChangeSpy).toHaveBeenCalledTimes(1);

    jest.resetAllMocks();

    fireEvent.click(screen.getByTestId('test-input'), { target: { value: 'some new text' } });

    expect(logTransport.handle).toHaveBeenCalledWith(
      expect.objectContaining({
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
            value: 'some new text',
          }),
        ]),
      })
    );
    expect(onBlurSpy).not.toHaveBeenCalled();
    expect(onChangeSpy).not.toHaveBeenCalled();
    expect(onClickSpy).toHaveBeenCalledTimes(1);
  });

  it('should allow forwarding refs', () => {
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new LogTransport() });
    const ref = createRef<HTMLInputElement>();

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputContext
          type={'text'}
          defaultValue={'test 1'}
          ref={ref}
          objectiv={{ Component: 'input', id: 'input-id' }}
        />
      </ObjectivProvider>
    );

    expect(ref.current).toMatchInlineSnapshot(`
      <input
        type="text"
        value="test 1"
      />
    `);
  });

  it('should execute the given onBlur as well', () => {
    const blurSpy = jest.fn();
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new LogTransport() });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedInputContext
          type={'text'}
          defaultValue={''}
          onBlur={blurSpy}
          data-testid={'test-input'}
          objectiv={{ Component: 'input', id: 'input-id' }}
        />
      </ObjectivProvider>
    );

    fireEvent.blur(screen.getByTestId('test-input'), { target: { value: 'some text' } });

    expect(blurSpy).toHaveBeenCalledTimes(1);
  });
});
