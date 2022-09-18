/*
 * Copyright 2021-2022 Objectiv B.V.
 */

/**
 * Set package version in globals
 */
import pkg from '../package.json';
globalThis.objectiv = globalThis.objectiv ?? {};
globalThis.objectiv.versions = globalThis.objectiv.versions ?? new Map();
globalThis.objectiv.versions.set(pkg.name, pkg.version);

export * from '@objectiv/tracker-react-core';

export * from './common/factories/makeAnchorClickHandler';
export * from './common/factories/makeReactTrackerDefaultPluginsList';
export * from './common/factories/makeReactTrackerDefaultQueue';
export * from './common/factories/makeReactTrackerDefaultTransport';

export * from './trackedContexts/TrackedContentContext';
export * from './trackedContexts/TrackedExpandableContext';
export * from './trackedContexts/TrackedInputContext';
export * from './trackedContexts/TrackedLinkContext';
export * from './trackedContexts/TrackedMediaPlayerContext';
export * from './trackedContexts/TrackedOverlayContext';
export * from './trackedContexts/TrackedNavigationContext';
export * from './trackedContexts/TrackedPressableContext';
export * from './trackedContexts/TrackedRootLocationContext';

export * from './trackedElements/TrackedAnchor';
export * from './trackedElements/TrackedButton';
export * from './trackedElements/TrackedDiv';
export * from './trackedElements/TrackedFooter';
export * from './trackedElements/TrackedHeader';
export * from './trackedElements/TrackedInput';
export * from './trackedElements/TrackedInputCheckbox';
export * from './trackedElements/TrackedInputRadio';
export * from './trackedElements/TrackedMain';
export * from './trackedElements/TrackedNav';
export * from './trackedElements/TrackedSection';
export * from './trackedElements/TrackedSelect';

export * from './ReactTracker';
export * from './types';
