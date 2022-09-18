/*
 * Copyright 2022 Objectiv B.V.
 */

const cheerio = require('cheerio');
const axios = require('axios');
const fs = require('fs');

/**
 * Script to fetch, parse and generate country codes definitions for LocaleContext Plugin.
 * Execute directly with node (node src/generateCountryCodes.js), or via `yarn generate:country-codes`.
 */

const COUNTRY_CODES_PAGE = 'https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2';
const DESTINATION_FILENAME = '../../plugins/locale-context/src/generated/CountryCodes.ts';

try {
  axios({
    method: 'GET',
    url: COUNTRY_CODES_PAGE,
  }).then(({ data }) => {
    const $ = cheerio.load(data);

    // Get the table we are interested in by finding its `caption`
    const table = $('caption:contains("Decoding table of ISO 3166-1 alpha-2 codes")').parent();

    // Find all `a` in a `td` with the `active` class, meaning "officially assigned"
    const activeCountryLinks = table.find(`td.active a`);

    // Get `a`s contents as text and convert to array, then sort it alphabetically
    const countryCodes = activeCountryLinks
      .map((_, td) => $(td).text())
      .toArray()
      .sort();

    fs.writeFileSync(DESTINATION_FILENAME, `/*\n * Copyright ${new Date().getFullYear()} Objectiv B.V.\n */\n\n`);

    fs.appendFileSync(
      DESTINATION_FILENAME,
      `/**\n * Do not edit this module.\n * Run its generator utility instead: core/utilities/src/generateCountryCodes.ts.\n */\n\n`
    );

    fs.appendFileSync(
      DESTINATION_FILENAME,
      `export const CountryCodes = [\n  '${countryCodes.join(`',\n  '`)}',\n];\n`
    );

    console.log(`Country Codes saved to ${DESTINATION_FILENAME}.`);
  });
} catch (err) {
  console.log(`Could not generate Country Codes.`);
  console.error(err);
}
