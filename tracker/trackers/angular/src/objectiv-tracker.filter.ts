/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { Pipe, PipeTransform } from '@angular/core';
import { makeId } from '@objectiv/tracker-browser';

/**
 * A PipeTransform to convert the given string in an id-like string using Core Tracker makeId
 */
@Pipe({
  name: 'makeId',
})
export class MakeId implements PipeTransform {
  transform(input: string | number, normalize: boolean = true): string | null {
    return makeId(input, normalize);
  }
}
