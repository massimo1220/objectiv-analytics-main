/*
 * Copyright 2022 Objectiv B.V.
 */

import { AbstractGlobalContext } from '@objectiv/schema';
import {
  GlobalContextErrorType,
  GlobalContextName,
  TrackerEvent,
  UniqueGlobalContextValidationRuleFactory,
} from '@objectiv/tracker-core';
import { EventRecorder } from '../EventRecorder';
import { GlobalContextErrorMessages } from '../generated/ContextErrorMessages';
import { TrackerConsole } from '../TrackerConsole';

/**
 * A generic Rule that can verify and console error when a GlobalContext is present multiple times
 */
export const makeUniqueGlobalContextValidationRule: UniqueGlobalContextValidationRuleFactory = (parameters) => {
  const validationRuleName = `UniqueGlobalContextValidationRule`;
  const errorType = GlobalContextErrorType.GLOBAL_CONTEXT_DUPLICATED;

  TrackerConsole.groupCollapsed(`｢objectiv:${parameters.logPrefix?.concat(':')}${validationRuleName}｣ Initialized.`);
  TrackerConsole.group(`Parameters:`);
  TrackerConsole.log(parameters);
  TrackerConsole.groupEnd();
  TrackerConsole.groupEnd();

  return {
    validationRuleName,
    ...parameters,

    /**
     * Verifies whether the given Context is present or duplicated in the given TrackerEvent.
     */
    validate(event: TrackerEvent): void {
      if (parameters.eventMatches && !parameters.eventMatches(event)) {
        return;
      }

      const seenGlobalContexts: AbstractGlobalContext[] = [];
      const duplicateGlobalContexts = event.global_contexts.filter((globalContext) => {
        if (
          seenGlobalContexts.find(
            (seenGlobalContext) =>
              seenGlobalContext._type === globalContext._type && seenGlobalContext.id === globalContext.id
          )
        ) {
          return true;
        }

        seenGlobalContexts.push(globalContext);
        return false;
      });

      duplicateGlobalContexts.forEach((globalContext) => {
        const globalContextName = globalContext._type as GlobalContextName;
        const errorMessagePrefix = `｢objectiv${this.logPrefix ? ':' + this.logPrefix : ''}｣`;
        const errorMessageTemplate = GlobalContextErrorMessages[this.platform][errorType][globalContextName];
        const errorMessageBody = errorMessageTemplate
          .replace(/{{contextIds}}/g, `(id: ${globalContext.id})`)
          .replace(/{{eventName}}/g, event._type);

        const errorMessage = `%c${errorMessagePrefix} Error: ${errorMessageBody}`;

        EventRecorder.error(errorMessage);

        TrackerConsole.groupCollapsed(errorMessage, 'color:red');
        TrackerConsole.group(`Event:`);
        TrackerConsole.log(event);
        TrackerConsole.groupEnd();
        TrackerConsole.groupEnd();
      });
    },
  };
};
