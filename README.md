<a href="https://objectiv.io">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://user-images.githubusercontent.com/82152911/159266895-39f52604-83c1-438d-96bd-9a6d66e74b08.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://user-images.githubusercontent.com/82152911/159266790-19e0e3d4-0d10-4c58-9da7-16edde9ec05a.svg">
  <img alt="Objectiv logo" src="https://user-images.githubusercontent.com/82152911/159266790-19e0e3d4-0d10-4c58-9da7-16edde9ec05a.svg">
</picture>

</a>

[Objectiv](https://objectiv.io/) is an open-source data collection & modeling platform for product analytics. It enables data teams to run product analytics from their notebooks with full control over data and models.

![image](https://user-images.githubusercontent.com/82152911/187921808-24c8dab7-8410-4f35-b609-e9ce4a893cfc.png)

* **Build BI dashboards for your teams in minutes** - Take pre-built analytics models (or build your own) and turn them into production-ready SQL with one command.
* **Explore and model with zero grunt work** - Work directly on super-structured  raw data that’s designed for modeling. No cleaning or transformations required.
* **Set up error-free tracking with strict validation tools** - Get helpful tooling to test, validate and debug your tracking setup at multiple stages. No more surprises downstream.


---

## Getting started

1. Install the open model hub from PyPI:

```sh
pip install objectiv-modelhub
```

2. [Read how to get started in your notebook](https://objectiv.io/docs/modeling/get-started-in-your-notebook/) in the docs.

### See also:

* [Demo notebooks](https://objectiv.io/docs/modeling/example-notebooks) - See Objectiv in action.
* [Objectiv Docs](https://www.objectiv.io/docs) - Technical documentation.
* [Objectiv on Slack](https://objectiv.io/join-slack) - Learn & share about Objectiv and product analytics modeling.

---

## What's in the box?

* **A taxonomy** to give your datasets a generic & strict event structure designed for modeling.
* **Tracking SDKs** for modern front-end frameworks to collect error-free user behavior data.
* **An open model hub** with pre-built product analytics models & operations.
* **A modeling library** to create reusable models that run on your full dataset.

<a href="https://objectiv.io">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://user-images.githubusercontent.com/82152911/184355794-4b957f62-210c-4a66-bda6-6405ab8f8a3e.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://user-images.githubusercontent.com/82152911/184355849-ee1c59af-068e-48e0-bcd3-b064633d2fa7.svg">
  <img alt="Objectiv stack" src="https://user-images.githubusercontent.com/82152911/184355849-ee1c59af-068e-48e0-bcd3-b064633d2fa7.svg">
</picture>

</a>

### The open analytics taxonomy

Objectiv is built around an [open analytics taxonomy](https://www.objectiv.io/docs/taxonomy): a universal structure for analytics data that has been designed and tested with UIs and analytics use cases of over 50 companies. It ensures your dataset covers a wide range of common analytics use cases and is structured with modeling in mind. You can extend it to cover custom requirements as well.

[![taxonomy](https://user-images.githubusercontent.com/82152911/162000133-1eea0192-c882-4121-a866-8c1a3f8ffee3.svg)](https://www.objectiv.io/docs/taxonomy)

Datasets that embrace the taxonomy are highly consistent. As a result, models built on one dataset can be deployed and run on another.

We're continuously expanding the coverage of the open analytics taxonomy. Support for marketing campaign analysis has been added recently, and areas like payments & CRM are on the roadmap.

### Tracking SDKs

Supports front-end engineers to [implement tracking instrumentation](https://www.objectiv.io/docs/tracking) that embraces the open analytics taxonomy.

* Provides validation and end-to-end testing tooling to set up error-free instrumentation.
* Support for React, React Native, Angular & JS, and expanding.
 
### Open model hub

A [growing collection of pre-built product analytics models and functions](https://objectiv.io/docs/modeling/open-model-hub/). You can take and run them directly, or incorporate them into your own custom models.

* Covers a wide range of use cases: from basic product analytics to predictive analysis with ML.
* Works with any dataset that embraces the open analytics taxonomy.
* New models & functions are added continuously.

### Bach modeling library

A pandas-like [modeling library](https://www.objectiv.io/docs/modeling/bach/) to build models that run on the full SQL dataset.

* Includes specific operations to easily work with datasets that embrace the open analytics taxonomy.
* Pandas-compatible: use popular pandas ML libraries in your models.
* Output models to production SQL directly, to simplify data debugging & delivery to BI tools, dbt, etc. 

---

## Stack compatibility

Objectiv plays nice with most popular tools in the modern data stack.

![image](https://user-images.githubusercontent.com/82152911/187926331-1428acd1-e350-48f3-9b7c-c9db35f14972.png)


---

This repository is part of the source code for Objectiv, which is released under the Apache 2.0 License. Please refer to [LICENSE.md](LICENSE.md) for details.
