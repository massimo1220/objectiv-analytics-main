/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { LocationTaggerParameters } from './LocationTaggerParameters';

/**
 * tagLink has one extra attribute, `href`, as mandatory parameter.
 */
export type TagLinkParameters = LocationTaggerParameters & { href: string };
