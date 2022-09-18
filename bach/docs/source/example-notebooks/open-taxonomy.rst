.. _example_open_taxonomy:

.. frontmatterposition:: 9

.. currentmodule:: bach

====================
Open taxonomy how-to
====================

This notebook demonstrates what you can do with the :doc:`Bach modeling library <../bach/index>` and a 
dataset that is validated against the `open analytics taxonomy <https://objectiv.io/docs/taxonomy/>`_. 

It's also available in a 
`notebook <https://github.com/objectiv/objectiv-analytics/blob/main/notebooks/open-taxonomy-how-to.ipynb>`_
to run on your own data, or you can instead `run the Demo </docs/home/try-the-demo/>`_ to quickly try it 
out.

The Objectiv :doc:`Bach API <../bach/api-reference/index>` is strongly pandas-like, to provide a familiar 
interface to handle large amounts of data in a python environment, while supporting multiple data stores. See 
`an intro into the pandas API here <https://pandas.pydata.org/pandas-docs/stable/user_guide/10min.html>`_.

This example uses real data collected with Objectiv's `Tracking SDK <https://objectiv.io/docs/tracking/>`_ on 
objectiv.io, stored in an SQL database.

Getting started
---------------
First we have to install the open model hub and instantiate the Objectiv DataFrame object; see
:doc:`getting started in your notebook <../get-started-in-your-notebook>`.

The open model hub is a toolkit with functions and models that can run directly on a full dataset collected 
with Objectiv's Tracker SDKs. The :doc:`get_objectiv_dataframe() 
<../open-model-hub/api-reference/ModelHub/modelhub.ModelHub.get_objectiv_dataframe>` operation creates a Bach 
DataFrame that has all columns and data types set correctly, and as such can always be used with models from 
the open model hub. 

By instantiating the model hub with a `global_contexts` parameter, all global contexts that are needed in the 
following analyses are added to the DataFrame. In this example, we select 'application' and 'marketing' 
contexts. :ref:`Later in this notebook <global_contexts>` we'll give more details on what data is available 
in the global contexts and how to access this data for analyses.

.. doctest::
	:skipif: engine is None

	>>> # set the timeframe of the analysis
	>>> start_date = '2022-03-01'
	>>> end_date = None

.. we override the timeframe for the doctests below
	
.. testsetup:: open-taxonomy
	:skipif: engine is None

	start_date = '2022-06-01'
	end_date = '2022-06-30'

.. doctest:: open-taxonomy
	:skipif: engine is None

	>>> from modelhub import ModelHub, display_sql_as_markdown
	>>> # instantiate the model hub, set the default time aggregation to daily
	>>> # and get the global contexts that will be used in this example
	>>> modelhub = ModelHub(time_aggregation='%Y-%m-%d', global_contexts=['application', 'marketing'])
	>>> # get an Objectiv DataFrame within a defined timeframe
	>>> df = modelhub.get_objectiv_dataframe(db_url=DB_URL, start_date=start_date, end_date=end_date)

The data for this DataFrame is still in the database, and the database is not queried before any of the data 
is loaded to the python environment. The methods that query the database are: 

* :doc:`head <../bach/api-reference/DataFrame/bach.DataFrame.head>`
* :doc:`to_pandas <../bach/api-reference/DataFrame/bach.DataFrame.to_pandas>`
* :doc:`get_sample <../bach/api-reference/DataFrame/bach.DataFrame.get_sample>`
* :doc:`to_numpy <../bach/api-reference/DataFrame/bach.DataFrame.to_numpy>`
* The property accessors :doc:`Series.array <../bach/api-reference/Series/bach.Series.array>`, and 
	:doc:`Series.value <../bach/api-reference/Series/bach.Series.value>`

For demo purposes of this notebook, these methods are called often to show the results of our operations. To 
limit the number of executed queries on the full dataset, it is recommended to use these methods less often or 
:ref:`to sample the data first <sampling>`.

.. admonition:: Reference
	:class: api-reference

	* :doc:`modelhub.ModelHub.get_objectiv_dataframe <../open-model-hub/api-reference/ModelHub/modelhub.ModelHub.get_objectiv_dataframe>`

The data
--------
The DataFrame contains:

* The index. This is a unique identifier for every hit.

.. doctest:: open-taxonomy
	:skipif: engine is None

	>>> df.index_dtypes
	{'event_id': 'uuid'}

* The event data. These columns contain all information about the event.

.. doctest:: open-taxonomy
	:skipif: engine is None

	>>> df.dtypes
	{'day': 'date',
	 'moment': 'timestamp',
	 'user_id': 'uuid',
	 'location_stack': 'objectiv_location_stack',
	 'event_type': 'string',
	 'stack_event_types': 'json',
	 'session_id': 'int64',
	 'session_hit_number': 'int64',
	 'application': 'objectiv_global_context',
	 'marketing': 'objectiv_global_context'}


What's in these columns:

- `day`: the day of the session as a date.
- `moment`: the exact moment of the event.
- `user_id`: the unique identifier of the user based on the cookie.
- `location_stack`: a JSON-like data column that stores information on the exact location where the event is 
	triggered in the product's UI. :ref:`See below for a more detailed explanation <location_stack>`.
- `event_type`: the type of event that is logged.
- `stack_event_types`: the parents of the event_type.
- `session_id`: a unique incremented integer id for each session. Starts at 1 for the selected data in the DataFrame.
- `session_hit_number`: a incremented integer id for each hit in session ordered by moment.

Besides these 'standard' columns, the DataFrame contains additional columns that are extracted from the global contexts:

* `application`
* `marketing`

:ref:`See more about global contexts here <global_contexts>`.

A preview of the data below, showing the latest PressEvents.

.. doctest:: open-taxonomy
	:skipif: engine is None

	>>> df[df.event_type == 'PressEvent'].sort_values('moment', ascending=False).head()
	                                             day                  moment                               user_id                                     location_stack  event_type                              stack_event_types  session_id  session_hit_number                                        application marketing
	event_id
	252d7d87-5600-4d90-b24f-2a6fb8986c5e  2022-06-30 2022-06-30 21:40:30.117  2d718142-9be7-4975-a669-ba022fd8fd48  [{'id': 'home', '_type': 'RootLocationContext'...  PressEvent  [AbstractEvent, InteractiveEvent, PressEvent]         872                   2  [{'id': 'objectiv-website', '_type': 'Applicat...        []
	157a3000-bbfc-42e0-b857-901bd578ea7c  2022-06-30 2022-06-30 21:40:16.908  2d718142-9be7-4975-a669-ba022fd8fd48  [{'id': 'home', '_type': 'RootLocationContext'...  PressEvent  [AbstractEvent, InteractiveEvent, PressEvent]         872                   1  [{'id': 'objectiv-website', '_type': 'Applicat...        []
	835b918b-23a3-46ce-b959-337adc9511de  2022-06-30 2022-06-30 19:52:41.870  549c8309-0851-4253-b11c-a41230c6d273  [{'id': 'home', '_type': 'RootLocationContext'...  PressEvent  [AbstractEvent, InteractiveEvent, PressEvent]         870                   1  [{'id': 'objectiv-website', '_type': 'Applicat...        []
	d8969faa-af29-4b9a-8dbe-6244c30953dc  2022-06-30 2022-06-30 17:14:29.033  5f5b80ec-f14f-4e81-a8f4-7015ba4c0b47  [{'id': 'tracking', '_type': 'RootLocationCont...  PressEvent  [AbstractEvent, InteractiveEvent, PressEvent]         868                  38  [{'id': 'objectiv-docs', '_type': 'Application...        []
	7f87a658-666c-4a81-8da3-8d134d91856b  2022-06-30 2022-06-30 17:14:28.471  5f5b80ec-f14f-4e81-a8f4-7015ba4c0b47  [{'id': 'taxonomy', '_type': 'RootLocationCont...  PressEvent  [AbstractEvent, InteractiveEvent, PressEvent]         868                  37  [{'id': 'objectiv-docs', '_type': 'Application...        []

.. admonition:: Reference
	:class: api-reference

	* :doc:`bach.DataFrame.index_dtypes <../bach/api-reference/DataFrame/bach.DataFrame.index_dtypes>`
	* :doc:`bach.DataFrame.dtypes <../bach/api-reference/DataFrame/bach.DataFrame.dtypes>`
	* :doc:`bach.DataFrame.sort_values <../bach/api-reference/DataFrame/bach.DataFrame.sort_values>`
	* :doc:`bach.DataFrame.head <../bach/api-reference/DataFrame/bach.DataFrame.head>`

The Open Taxonomy
-----------------
Data in a DataFrame created with :doc:`get_objectiv_dataframe 
<../open-model-hub/api-reference/ModelHub/modelhub.ModelHub.get_objectiv_dataframe>` follows the 
`open analytics taxonomy <https://objectiv.io/docs/taxonomy/>`_:

* **event_type** column: describes the type of interactive or non-interactive event.
* **location_stack** column: describes where an event exactly happened in the user interface.
* **global contexts** data: general information about the state in which an event happened.

The following section goes through these concepts one-by-one.

event_type column
~~~~~~~~~~~~~~~~~
The `event_type` describes what type of event was triggered. The goal of the open taxonomy is to label all 
interactive and non-interactive events in a standardized way. Together with the `location_stack`, the 
`event_type` 'defines' what happened with, or on the product.

.. doctest:: open-taxonomy
	:skipif: engine is None

	>>> df[df.day == '2022-01-10'].event_type.head()
	Series([], Name: event_type, dtype: object)

.. _location-stack-and-global-contexts:

location stack and global contexts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The location stack and global contexts are stored as JSON type data. Within the DataFrame, it is easy to 
access data in JSON data based on position or content.

Slicing the JSON data
^^^^^^^^^^^^^^^^^^^^^
With the `.json[]` syntax you can slice the array using integers. Instead of integers, dictionaries can also 
be passed to 'query' the JSON array. If the passed dictionary matches a context object in the stack, all 
objects of the stack starting (or ending, depending on the slice) at that object will be returned.

**An example**

Consider a JSON array that looks like this (this is a real example of a location stack):

.. code-block:: json

	[{"id": "docs", "_type": "RootLocationContext"},
	 {"id": "docs-sidebar", "_type": "NavigationContext"},
	 {"id": "API Reference", "_type": "ExpandableContext"},
	 {"id": "DataFrame", "_type": "ExpandableContext"},
	 {"id": "Overview", "_type": "LinkContext"}]

**Regular slicing**

.. code-block:: python

	df.location_stack.json[2:4]

For the example array it would return:

.. code-block:: json

	[{"id": "API Reference", "_type": "ExpandableContext"},
	 {"id": "DataFrame", "_type": "ExpandableContext"}]

**Slicing by querying**

We want to return only the part of the array starting at the object that contain this object:

.. code-block:: javascript

	{"id": "docs-sidebar", "_type": "NavigationContext"}

The syntax for selecting like this is: 

.. code-block:: python

	df.location_stack.json[{"id": "docs-sidebar", "_type": "NavigationContext"}:]

For the example array it would return:

.. code-block:: json

	[{'id': 'docs-sidebar', '_type': 'NavigationContext'},
	 {'id': 'API Reference', '_type': 'ExpandableContext'},
	 {'id': 'DataFrame', '_type': 'ExpandableContext'},
	 {'id': 'Overview', '_type': 'LinkContext'}]

In case a JSON array does not contain the object, `None` is returned. More info at the 
:doc:`API reference <../bach/api-reference/Series/Json/index>`.

.. _location_stack:

location_stack column
~~~~~~~~~~~~~~~~~~~~~

The `location_stack` column in the DataFrame stores the information on where an event exactly happened in the 
user interface. The example used above is the location stack of a link to the DataFrame API reference, in the 
menu on our documentation pages.

Because of the specific way the location information is labeled, validated, and stored using the open 
analytics taxonomy, it can be used to easily slice and group your product's features. The column is set as an 
`objectiv_location_stack` type, and therefore location stack specific methods can be used to access the data 
from the `location_stack`. These :doc:`methods <../bach/api-reference/Series/Json/bach.SeriesJson.json>` can 
be used using the `.ls` accessor on the column:

* :doc:`.ls.navigation_features <../open-model-hub/api-reference/SeriesLocationStack/modelhub.SeriesLocationStack.ls>`
* :doc:`.ls.feature_stack <../open-model-hub/api-reference/SeriesLocationStack/modelhub.SeriesLocationStack.ls>`
* :doc:`.ls.nice_name <../open-model-hub/api-reference/SeriesLocationStack/modelhub.SeriesLocationStack.ls>`

For example:

.. code-block:: python
	
	df.location_stack.ls.nice_name

returns '*Link: Overview located at Root Location: docs => Navigation: docs-sidebar => Expandable: API 
Reference => Expandable: DataFrame*' for the location stack mentioned above.

`See the full reference of the location stack here <https://objectiv.io/docs/taxonomy/location-contexts/>`_. 
An example location stack for a PressEvent is queried below:

.. doctest:: open-taxonomy
	:skipif: engine is None

	>>> df[df.event_type == 'PressEvent'].location_stack.head(1)[0]
	[{'id': 'home', '_type': 'RootLocationContext', '_types': ['AbstractContext', 'AbstractLocationContext', 'RootLocationContext']}, {'id': 'navbar-top', '_type': 'NavigationContext', '_types': ['AbstractContext', 'AbstractLocationContext', 'NavigationContext']}, {'id': 'about-us', 'href': '/about', '_type': 'LinkContext', '_types': ['AbstractContext', 'AbstractLocationContext', 'LinkContext', 'PressableContext']}]

.. _global_contexts:

global_contexts
~~~~~~~~~~~~~~~
Global contexts contain all general information that is relevant to the logged event. To optimize data 
processing, not all data that is stored in the global contexts in the database is loaded into the DataFrame 
when it is created. Data columns are only created for the global contexts that are selected when the model 
hub is instantiated. In this example, those columns are `application` and `marketing`.

Each selected global context is a JSON-like column of the 'objectiv_global_context' type, and therefore 
contains multiple key-value pairs. The data in these JSON columns can be accessed with the `context` accessor 
on the respective columns. For example to get the ID of the application as a Series, you use:

.. code-block:: python

	df.application.context.id

Similarly, the application ID can be set as regular (text) column in the DataFrame:

.. code-block:: python

	df['application_id'] = df.application.context.id

`See the full reference of all available global contexts in the open taxonomy here 
<https://objectiv.io/docs/taxonomy/global-contexts/>`_. Each global context _always_ has an 'id' key that 
uniquely identifies the global context of that type. Additional keys are shown in the blocks of each context 
in the reference.

From the marketing context, for example, we can therefore also get the 'source' as a column:

.. code-block:: python

	df['marketing_source'] = df.marketing.context.source

When instantiating the model hub, global contexts are added using the name of the context without the word
'Context' and converted to 'snake_case' (the name of the context split before every capital letter and
joined with an underscore), i.e. to add the HttpContext use 'http' and to add the InputValueContext use
'input_value':

.. code-block:: python

	modelhub = ModelHub(global_contexts=['http', 'input_value'])

In the case you later want to add other data from the global contexts to your DataFrame, you will have to 
re-instantiate the model hub with those contexts and recreate the DataFrame. Note that no data has to be 
processed for recreating the DataFrame until the data gets queried (by using `.head()` or similar).

.. doctest:: open-taxonomy
	:skipif: engine is None

	>>> # we create the columns from the examples above, and show the data.
	>>> df['application_id'] = df.application.context.id
	>>> df['marketing_source'] = df.marketing.context.source

.. doctest:: open-taxonomy
	:skipif: engine is None

	>>> # we can now show the columns where the marketing source is not null.
	>>> df[df.marketing_source.notnull()][['application', 'marketing', 'application_id', 'marketing_source']].head()
	                                                                            application                                          marketing    application_id marketing_source
	event_id
	d1c72d21-4233-40dc-b93d-3323dbf4cf75  [{'id': 'objectiv-website', '_type': 'Applicat...  [{'id': 'utm', 'term': None, '_type': 'Marketi...  objectiv-website          twitter
	814f1861-c5b4-4f65-b475-2d37112b91de  [{'id': 'objectiv-website', '_type': 'Applicat...  [{'id': 'utm', 'term': None, '_type': 'Marketi...  objectiv-website         linkedin
	ada3c06a-e669-4588-803b-aea8768e575f  [{'id': 'objectiv-website', '_type': 'Applicat...  [{'id': 'utm', 'term': None, '_type': 'Marketi...  objectiv-website         linkedin
	63010d9d-730d-443f-9ba4-2c78ffe602cb  [{'id': 'objectiv-website', '_type': 'Applicat...  [{'id': 'utm', 'term': None, '_type': 'Marketi...  objectiv-website         linkedin
	02d31e6b-c668-47bb-b6f4-356d997f9863  [{'id': 'objectiv-website', '_type': 'Applicat...  [{'id': 'utm', 'term': None, '_type': 'Marketi...  objectiv-website         linkedin

.. admonition:: Reference
	:class: api-reference

	* :doc:`bach.DataFrame.head <../bach/api-reference/DataFrame/bach.DataFrame.head>`
	* :doc:`bach.Series.notnull <../bach/api-reference/Series/bach.Series.notnull>`

.. _sampling:

Sampling
--------
One of the key features to Objectiv Bach is that it runs on your full dataset. There can, however, be 
situations where you want to experiment with your data, meaning you have to query the full dataset often, 
which can become slow and/or costly.

To limit this, it's possible to do operations on a sample of the full dataset. All operations can easily be 
applied to the full dataset again at any time.

Below we create a sample that randomly selects ~1% of all the rows in the data, using the 
:doc:`get_sample() <../bach/api-reference/DataFrame/bach.DataFrame.get_sample>` operation. A table containing 
the sampled is written to the database, therefore the `table_name` must be provided when creating the sample.

.. NOTE: Because of random sampling, the following will never be deterministic if executed as a doctest, so 
	instead running most of it as a regular code-block

.. testsetup:: open-taxonomy-sampling
	:skipif: engine is None

	from modelhub import ModelHub
	def display_sql_as_markdown(arg):
		print('sql\\n' + arg.view_sql() + '\\n') # print out SQL instead of an object
	start_date = '2022-06-01'
	end_date = '2022-06-30'
	modelhub = ModelHub(time_aggregation='%Y-%m-%d', global_contexts=['application', 'marketing'])
	df = modelhub.get_objectiv_dataframe(db_url=DB_URL, start_date=start_date, end_date=end_date)
	df['application_id'] = df.application.context.id

.. doctest:: open-taxonomy-sampling
	:skipif: engine is None

	>>> # for BigQuery the table name should be 'YOUR_PROJECT.YOUR_WRITABLE_DATASET.YOUR_TABLE_NAME'
	>>> df_sample = df.get_sample(table_name='sample_data', sample_percentage=10, overwrite=True)

A new column is created in the sample.

.. code-block:: jupyter-notebook

	>>> df_sample['root_location_contexts'] = df_sample.location_stack.json[:1]
	>>> df_sample.sort_values('moment', ascending=False).head()
	
.. code-block:: jupyter-notebook-out

	                                             day                  moment                               user_id                                     location_stack              event_type                                  stack_event_types  session_id  session_hit_number                                        application marketing    application_id marketing_source                             root_location_contexts
	event_id                                                                                                                                                                                                                                                                                                                                                                                   
	157a3000-bbfc-42e0-b857-901bd578ea7c  2022-06-30 2022-06-30 21:40:16.908  2d718142-9be7-4975-a669-ba022fd8fd48  [{'id': 'home', '_type': 'RootLocationContext'...              PressEvent      [AbstractEvent, InteractiveEvent, PressEvent]         872                   1  [{'id': 'objectiv-website', '_type': 'Applicat...        []  objectiv-website             None  [{'id': 'home', '_type': 'RootLocationContext'...
	14d2fbb9-32f9-4031-955a-05935909d754  2022-06-30 2022-06-30 18:03:41.139  fdf31cae-4906-476a-b206-e0a9644ced52  [{'id': 'home', '_type': 'RootLocationContext'...  ApplicationLoadedEvent  [AbstractEvent, ApplicationLoadedEvent, NonInt...         869                   1  [{'id': 'objectiv-docs', '_type': 'Application...        []     objectiv-docs             None  [{'id': 'home', '_type': 'RootLocationContext'...
	7f87a658-666c-4a81-8da3-8d134d91856b  2022-06-30 2022-06-30 17:14:28.471  5f5b80ec-f14f-4e81-a8f4-7015ba4c0b47  [{'id': 'taxonomy', '_type': 'RootLocationCont...              PressEvent      [AbstractEvent, InteractiveEvent, PressEvent]         868                  37  [{'id': 'objectiv-docs', '_type': 'Application...        []     objectiv-docs             None  [{'id': 'taxonomy', '_type': 'RootLocationCont...
	454997de-09cb-440b-b288-83d48280e2d6  2022-06-30 2022-06-30 17:14:20.194  5f5b80ec-f14f-4e81-a8f4-7015ba4c0b47  [{'id': 'home', '_type': 'RootLocationContext'...            VisibleEvent  [AbstractEvent, NonInteractiveEvent, VisibleEv...         868                  33  [{'id': 'objectiv-docs', '_type': 'Application...        []     objectiv-docs             None  [{'id': 'home', '_type': 'RootLocationContext'...
	566c9831-582c-4ec3-861a-6893c65b7b29  2022-06-30 2022-06-30 17:14:13.815  5f5b80ec-f14f-4e81-a8f4-7015ba4c0b47  [{'id': 'home', '_type': 'RootLocationContext'...            VisibleEvent  [AbstractEvent, NonInteractiveEvent, VisibleEv...         868                  31  [{'id': 'objectiv-docs', '_type': 'Application...        []     objectiv-docs             None  [{'id': 'home', '_type': 'RootLocationContext'...

Using the :doc:`.get_unsampled() <../bach/api-reference/DataFrame/bach.DataFrame.get_unsampled>` operation, 
the operations that are done on the sample (the creation of the column), are applied to the entire data set:

.. doctest:: open-taxonomy-sampling
	:skipif: engine is None

	>>> df_unsampled = df_sample.get_unsampled()
	>>> df_unsampled.sort_values('moment', ascending=False).head()
	                                             day                  moment                               user_id                                                                                location_stack              event_type                                                 stack_event_types  session_id  session_hit_number                                                                                   application marketing    application_id
	event_id                                                                                                                                                                                                                                                                                                                                                                                                          
	96b5e709-bb8a-46de-ac82-245be25dac29  2022-06-30 2022-06-30 21:40:32.401  2d718142-9be7-4975-a669-ba022fd8fd48  [{'id': 'home', '_type': 'RootLocationContext', '_types': ['AbstractContext', 'AbstractLo...            VisibleEvent                [AbstractEvent, NonInteractiveEvent, VisibleEvent]         872                   3  [{'id': 'objectiv-website', '_type': 'ApplicationContext', '_types': ['AbstractContext', ...        []  objectiv-website
	252d7d87-5600-4d90-b24f-2a6fb8986c5e  2022-06-30 2022-06-30 21:40:30.117  2d718142-9be7-4975-a669-ba022fd8fd48  [{'id': 'home', '_type': 'RootLocationContext', '_types': ['AbstractContext', 'AbstractLo...              PressEvent                     [AbstractEvent, InteractiveEvent, PressEvent]         872                   2  [{'id': 'objectiv-website', '_type': 'ApplicationContext', '_types': ['AbstractContext', ...        []  objectiv-website
	157a3000-bbfc-42e0-b857-901bd578ea7c  2022-06-30 2022-06-30 21:40:16.908  2d718142-9be7-4975-a669-ba022fd8fd48  [{'id': 'home', '_type': 'RootLocationContext', '_types': ['AbstractContext', 'AbstractLo...              PressEvent                     [AbstractEvent, InteractiveEvent, PressEvent]         872                   1  [{'id': 'objectiv-website', '_type': 'ApplicationContext', '_types': ['AbstractContext', ...        []  objectiv-website
	8543f519-d3a4-4af6-89f5-cb04393944b8  2022-06-30 2022-06-30 20:43:50.962  bb127c9e-3067-4375-9c73-cb86be332660  [{'id': 'home', '_type': 'RootLocationContext', '_types': ['AbstractContext', 'AbstractLo...          MediaLoadEvent  [AbstractEvent, MediaEvent, MediaLoadEvent, NonInteractiveEvent]         871                   2  [{'id': 'objectiv-website', '_type': 'ApplicationContext', '_types': ['AbstractContext', ...        []  objectiv-website
	a0ad4364-57e0-4da9-a266-057744550cc2  2022-06-30 2022-06-30 20:43:49.820  bb127c9e-3067-4375-9c73-cb86be332660  [{'id': 'home', '_type': 'RootLocationContext', '_types': ['AbstractContext', 'AbstractLo...  ApplicationLoadedEvent      [AbstractEvent, ApplicationLoadedEvent, NonInteractiveEvent]         871                   1  [{'id': 'objectiv-website', '_type': 'ApplicationContext', '_types': ['AbstractContext', ...        []  objectiv-website

The sample can also be used for grouping and aggregating. The example below counts all hits and the unique 
`event_types` in the sample:

.. code-block:: jupyter-notebook
	
	>>> df_sample_grouped = df_sample.groupby(['application_id']).agg({'event_type':'nunique','session_hit_number':'count'})
	>>> df_sample_grouped.head()

.. code-block:: jupyter-notebook-out

	                  event_type_nunique  session_hit_number_count
	application_id
	objectiv-docs                      5                       399
	objectiv-website                   8                       235

.. testsetup:: open-taxonomy-sampling-grouped
	:skipif: engine is None

	from modelhub import ModelHub
	start_date = '2022-06-01'
	end_date = '2022-06-30'
	modelhub = ModelHub(time_aggregation='%Y-%m-%d', global_contexts=['application', 'marketing'])
	df = modelhub.get_objectiv_dataframe(db_url=DB_URL, start_date=start_date, end_date=end_date)
	df['application_id'] = df.application.context.id
	df_sample = df.get_sample(table_name='sample_data', sample_percentage=10, overwrite=True)
	df_sample['root_location_contexts'] = df_sample.location_stack.json[:1]
	df_sample_grouped = df_sample.groupby(['application_id']).agg({'event_type':'nunique','session_hit_number':'count'})

As can be seen from the counts, unsampling applies the transformation to the entire data set:

.. doctest:: open-taxonomy-sampling-grouped
	:skipif: engine is None

	>>> df_unsampled_grouped = df_sample_grouped.get_unsampled()
	>>> df_unsampled_grouped.head()
	                  event_type_nunique  session_hit_number_count
	application_id
	objectiv-docs                      8                      4106
	objectiv-website                  10                      2292

.. admonition:: Reference
	:class: api-reference

	* :doc:`bach.DataFrame.get_sample <../bach/api-reference/DataFrame/bach.DataFrame.get_sample>`
	* :doc:`bach.DataFrame.get_unsampled <../bach/api-reference/DataFrame/bach.DataFrame.get_unsampled>`
	* :doc:`bach.DataFrame.sort_values <../bach/api-reference/DataFrame/bach.DataFrame.sort_values>`
	* :doc:`bach.DataFrame.groupby <../bach/api-reference/DataFrame/bach.DataFrame.groupby>`
	* :doc:`bach.DataFrame.head <../bach/api-reference/DataFrame/bach.DataFrame.head>`

Get the SQL for any analysis
----------------------------

The SQL for any analysis can be exported with one command, so you can use models in production directly to 
simplify data debugging & delivery to BI tools like Metabase, dbt, etc. See how you can `quickly create BI 
dashboards with this <https://objectiv.io/docs/home/try-the-demo#creating-bi-dashboards>`_.

.. doctest:: open-taxonomy
	:hide:
	
	>>> def display_sql_as_markdown(arg): [print('sql\n' + arg.view_sql() + '\n')]

.. doctest:: open-taxonomy
	:skipif: engine is None

	>>> # show the underlying SQL for this dataframe - works for any dataframe/model in Objectiv
	>>> press_events = df[df.event_type == 'PressEvent'].sort_values('moment', ascending=False)
	>>> display_sql_as_markdown(press_events)
	sql
	WITH "getitem_where_boolean___f92bdc71cddb7f9b81ac2cdb4704ff35" AS (
	        SELECT "event_id" AS "event_id",
	               "day" AS "day",
	               "moment" AS "moment",
	               "cookie_id" AS "user_id",
	               "value"->>'_type' AS "event_type",
	               cast("value"->>'_types' AS JSONB) AS "stack_event_types",
	               cast("value"->>'location_stack' AS JSONB) AS "location_stack",
	               cast("value"->>'time' AS bigint) AS "time",
	               jsonb_path_query_array(cast("value"->>'global_contexts' AS JSONB), '$[*] ? (@._type == $type)', '{"type":"ApplicationContext"}') AS "application",
	               jsonb_path_query_array(cast("value"->>'global_contexts' AS JSONB), '$[*] ? (@._type == $type)', '{"type":"MarketingContext"}') AS "marketing"
	          FROM "data"
	         WHERE ((("day" >= cast('2022-06-01' AS date))) AND (("day" <= cast('2022-06-30' AS date))))
	       ),
	       "context_data___0759f5311fed0efedf7414a86d3b98cc" AS (
	        SELECT "event_id" AS "event_id",
	               "day" AS "day",
	               "moment" AS "moment",
	               "user_id" AS "user_id",
	               "location_stack" AS "location_stack",
	               "event_type" AS "event_type",
	               "stack_event_types" AS "stack_event_types",
	               "application" AS "application",
	               "marketing" AS "marketing"
	          FROM "getitem_where_boolean___f92bdc71cddb7f9b81ac2cdb4704ff35"
	       ),
	       "session_starts___f9b9e531f71d1a32f060d7eaeeaf259e" AS (
	        SELECT "event_id" AS "event_id",
	               "day" AS "day",
	               "moment" AS "moment",
	               "user_id" AS "user_id",
	               "location_stack" AS "location_stack",
	               "event_type" AS "event_type",
	               "stack_event_types" AS "stack_event_types",
	               "application" AS "application",
	               "marketing" AS "marketing",
	               CASE WHEN (extract(epoch FROM (("moment") - (lag("moment", 1, cast(NULL AS TIMESTAMP WITHOUT TIME ZONE)) OVER (PARTITION BY "user_id" ORDER BY "moment" ASC NULLS LAST, "event_id" ASC NULLS LAST RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)))) <= cast(1800 AS bigint)) THEN cast(NULL AS boolean)
	                    ELSE cast(TRUE AS boolean)
	                     END AS "is_start_of_session"
	          FROM "context_data___0759f5311fed0efedf7414a86d3b98cc"
	       ),
	       "session_id_and_count___53c8cadbeb95a0cfb2c62b683ec62d05" AS (
	        SELECT "event_id" AS "event_id",
	               "day" AS "day",
	               "moment" AS "moment",
	               "user_id" AS "user_id",
	               "location_stack" AS "location_stack",
	               "event_type" AS "event_type",
	               "stack_event_types" AS "stack_event_types",
	               "application" AS "application",
	               "marketing" AS "marketing",
	               "is_start_of_session" AS "is_start_of_session",
	               CASE WHEN "is_start_of_session" THEN row_number() OVER (PARTITION BY "is_start_of_session" ORDER BY "moment" ASC NULLS LAST, "event_id" ASC NULLS LAST RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
	                    ELSE cast(NULL AS bigint)
	                     END AS "session_start_id",
	               count("is_start_of_session") OVER (ORDER BY "user_id" ASC NULLS LAST, "moment" ASC NULLS LAST, "event_id" ASC NULLS LAST RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS "is_one_session"
	          FROM "session_starts___f9b9e531f71d1a32f060d7eaeeaf259e"
	       ),
	       "objectiv_sessionized_data___498c4b8bb62268d87cf3f755d64fb0ec" AS (
	        SELECT "event_id" AS "event_id",
	               "day" AS "day",
	               "moment" AS "moment",
	               "user_id" AS "user_id",
	               "location_stack" AS "location_stack",
	               "event_type" AS "event_type",
	               "stack_event_types" AS "stack_event_types",
	               "application" AS "application",
	               "marketing" AS "marketing",
	               "is_start_of_session" AS "is_start_of_session",
	               "session_start_id" AS "session_start_id",
	               "is_one_session" AS "is_one_session",
	               first_value("session_start_id") OVER (PARTITION BY "is_one_session" ORDER BY "moment" ASC NULLS LAST, "event_id" ASC NULLS LAST RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS "session_id",
	               row_number() OVER (PARTITION BY "is_one_session" ORDER BY "moment" ASC NULLS LAST, "event_id" ASC NULLS LAST RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS "session_hit_number"
	          FROM "session_id_and_count___53c8cadbeb95a0cfb2c62b683ec62d05"
	       ),
	       "getitem_where_boolean___0bfa91dd039ab531a9a97022615a5196" AS (
	        SELECT "event_id" AS "event_id",
	               "day" AS "day",
	               "moment" AS "moment",
	               "user_id" AS "user_id",
	               "location_stack" AS "location_stack",
	               "event_type" AS "event_type",
	               "stack_event_types" AS "stack_event_types",
	               "session_id" AS "session_id",
	               "session_hit_number" AS "session_hit_number",
	               "application" AS "application",
	               "marketing" AS "marketing",
	               "application"->0->>'id' AS "application_id",
	               "marketing"->0->>'source' AS "marketing_source"
	          FROM "objectiv_sessionized_data___498c4b8bb62268d87cf3f755d64fb0ec"
	         WHERE ("event_type" = 'PressEvent')
	       ) SELECT "event_id" AS "event_id",
	       "day" AS "day",
	       "moment" AS "moment",
	       "user_id" AS "user_id",
	       "location_stack" AS "location_stack",
	       "event_type" AS "event_type",
	       "stack_event_types" AS "stack_event_types",
	       "session_id" AS "session_id",
	       "session_hit_number" AS "session_hit_number",
	       "application" AS "application",
	       "marketing" AS "marketing",
	       "application_id" AS "application_id",
	       "marketing_source" AS "marketing_source"
	  FROM "getitem_where_boolean___0bfa91dd039ab531a9a97022615a5196"
	 ORDER BY "moment" DESC NULLS LAST
	<BLANKLINE>


Where to go next
----------------
To dive further into working with the open taxonomy, 
:doc:`see the Bach API reference <../bach/api-reference/index>`.

You can also have a look at 
:doc:`the example notebook demonstrating the open model hub basics <./modelhub-basics>`.
