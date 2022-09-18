"""
Copyright 2022 Objectiv B.V.
"""

import bach
from bach.series import Series
from bach.expression import Expression, join_expressions
from sql_models.constants import NotSet, not_set
from typing import List, Union, TYPE_CHECKING, cast

from modelhub.util import check_groupby

if TYPE_CHECKING:
    from modelhub.series import SeriesLocationStack


GroupByType = Union[List[Union[str, Series]], str, Series, NotSet]


class FunnelDiscovery:
    """
    Class to discovery user journeys for funnel analysis.

    The main method of this class is the `get_navigation_paths`, to get the navigation
    paths of the users. This method can also get 'filtered' navigation paths to the
    conversion locations.

    For the visualization of the user flow, use the `plot_sankey_diagram` method.
    """

    CONVERSTION_STEP_COLUMN = '_first_conversion_step_number'

    FEATURE_NICE_NAME_SERIES = '__feature_nice_name'
    STEP_OFFSET_SERIES = '__root_step_offset'

    def _filter_navigation_paths_to_conversion(
        self,
        steps_df: bach.DataFrame,
        step_series_name: List[str],
    ) -> bach.DataFrame:
        """
        Filter each navigation path to first conversion location.

        For each row of steps_df dataframe set to None the step values
         after encountering the first conversion location step.

        Corner case: in case the first location stack is conversion one we ignore it
        and proceed to the next step.

        :param steps_df: dataframe which one gets from `FunnelDiscovery.get_navigation_paths`
            method, the dataframe that we're going to filter.

        :returns: bach DataFrame, filtered each row of steps_df to the conversion location.
        """

        conv_step_num_column = self.CONVERSTION_STEP_COLUMN
        if conv_step_num_column not in steps_df.data_columns:
            raise ValueError(f'{conv_step_num_column} column is missing in the dataframe.')

        result_df = steps_df[steps_df[conv_step_num_column] != 1]

        for step_name in step_series_name:
            tag = int(step_name.split('_')[-1])
            mask = (tag > result_df[conv_step_num_column]) | (result_df[conv_step_num_column].isnull())
            # don't consider any step happened after the first conversion step
            result_df.loc[mask, step_name] = None

        result_df = result_df.dropna(subset=[conv_step_num_column])
        return result_df

    def _construct_source_target_df(
            self,
            steps_df: bach.DataFrame,
            n_top_examples: int = None,
    ) -> bach.DataFrame:
        """
        Out of `steps_df` Bach dataframe we construct a new Bach dataframe with the following structure:

        - `'source', 'target', 'value'`
        - `'step1', 'step2', 'val1'`
        - `'step2', 'step3', 'val2'`
        - `'...', '...', '...'`

        The navigation steps are our nodes (source and target), the value shows
        how many source -> target links we have.

        :param steps_df: the dataframe from `FunnelDiscovery.get_navigation_paths`.
        :param n_top_examples: number of top navigation paths.

        :returns: Bach DataFrame with `source`, `target` and `value` columns.
        """

        import re
        from collections import defaultdict
        _IS_STEP_SERIES_REGEX = re.compile(r'(?P<root_series_name>.+)_step_(?P<step_number>\d+)')
        root_series_x_steps = defaultdict(list)

        # dataframe can contain steps from different roots, for now lets raise an error if
        # that is the case
        for series_name in steps_df.data_columns:
            match = _IS_STEP_SERIES_REGEX.match(series_name)
            if not match:
                continue

            r_series_name, step_number = match.groups()
            root_series_x_steps[r_series_name].append(int(step_number))

        if len(root_series_x_steps) == 0:
            raise ValueError('Couldn\'t find any navigation path.')

        if len(root_series_x_steps) > 1:
            raise ValueError(
                'Provided DataFrame contains navigation paths from multiple base series,'
                ' e.g. x_step_1, y_step_1, ... x_step_n, y_step_n.'
            )

        step_root_name = list(root_series_x_steps.keys())[0]
        step_numbers = root_series_x_steps[step_root_name]
        columns = [f'{step_root_name}_step_{i}' for i in step_numbers]

        # count navigation paths
        steps_counter_df = steps_df[columns].value_counts().reset_index()

        steps_counter_df = cast(bach.DataFrame, steps_counter_df)  # help mypy
        steps_counter_df = steps_counter_df.sort_values(['value_counts'] + columns,
                                                        ascending=False)
        steps_counter_df = steps_counter_df.materialize(limit=n_top_examples)

        step_size = 1  # we want steps' pairs
        all_dfs = []
        for i_step in range(1, max(step_numbers) - step_size + 1):
            step1 = f'location_stack_step_{i_step}'
            step2 = f'location_stack_step_{i_step + step_size}'

            column_names = {step1: 'source', step2: 'target'}
            _df = steps_counter_df[[step1, step2, 'value_counts']].rename(columns=column_names)
            all_dfs.append(_df.dropna())

        from bach.operations.concat import DataFrameConcatOperation
        result = DataFrameConcatOperation(objects=all_dfs, ignore_index=True)()
        links_df = result.groupby(['source', 'target']).agg('sum').reset_index().rename(
            columns={'value_counts_sum': 'value'}).sort_values('value', ascending=False)

        return links_df

    def get_navigation_paths(
        self,
        data: bach.DataFrame,
        steps: int,
        by: GroupByType = not_set,
        location_stack: 'SeriesLocationStack' = None,
        add_conversion_step_column: bool = False,
        only_converted_paths: bool = False,
        start_from_end: bool = False,
        n_examples: int = None
    ) -> bach.DataFrame:
        """
        Get the navigation paths for each event's location stack. Each navigation path
        is represented as a row, where each step is defined by the nice name of the
        considered location.

        For each location stack:

        - The number of navigation paths to be generated is less than or equal to
            `steps`.
        - The locations to be considered as starting steps are those that have
            an offset between 0 and `steps - 1` in the location stack.
        - For each path, the rest of steps are defined by the `steps - 1` locations
            that follow the start location in the location stack.

        For example, having `location_stack = ['a', 'b', 'c' , 'd']` and `steps` = 3
        will generate the following paths:

        - `'a', 'b', 'c'`
        - `'b', 'c', 'd'`
        - `'c', 'd', None`

        :param data: :py:class:`bach.DataFrame` to apply the method on.
        :param steps: Number of steps/locations to consider in navigation path.
        :param by: sets the column(s) to group by. If by is None or not set,
            then steps are based on the order of events based on the entire dataset.
        :param location_stack: the location stack

            - can be any slice of a :py:class:`modelhub.SeriesLocationStack` type column
            - if None - the whole location stack is taken.

        :param add_conversion_step_column: if True gets the first conversion step number
            per each navigation path and adds it as a column to the returned dataframe.
        :param only_converted_paths: if True filters each navigation path to first
            conversion location.
        :param start_from_end: if True starts the construction of navigation paths from the last
                context from the stack, otherwise it starts from the first.
                If there are too many steps, and we limit the amount with `n_examples` parameter
                we can lose the last steps of the user, hence in order to 'prioritize' the last
                steps one can use this parameter.

                Having `location_stack = ['a', 'b', 'c' , 'd']` and `steps` = 3
                will generate the following paths:

                    - `'b', 'c', 'd'`
                    - `'a', 'b', 'c'`
                    - `None, 'a', 'b'`

        :param n_examples: limit the amount of navigation paths.
                           If `None`, all the navigation paths are taken.

        :returns: Bach DataFrame containing a new Series for each step containing the nice name
            of the location.
        """
        from modelhub.util import check_objectiv_dataframe
        from modelhub.series.series_objectiv import SeriesLocationStack

        # check all parameters are correct
        if (
            (add_conversion_step_column or only_converted_paths)
            and 'is_conversion_event' not in data.data_columns
        ):
            raise ValueError('The is_conversion_event column is missing in the dataframe.')

        check_objectiv_dataframe(df=data, columns_to_check=['location_stack', 'moment'])
        _location_stack = location_stack or data['location_stack']
        _location_stack = _location_stack.copy_override_type(SeriesLocationStack)

        gb_series_names = []
        if by is not None and by is not not_set:
            valid_gb = check_groupby(data=data, groupby=by, not_allowed_in_groupby=_location_stack.name)
            gb_series_names = valid_gb.index_columns

        result = self._generate_navigation_steps(
            data=data,
            steps=steps,
            by=gb_series_names,
            location_stack=_location_stack,
            start_from_end=start_from_end,
            add_first_conversion_column=add_conversion_step_column or only_converted_paths,
        )

        # limit rows
        if n_examples is not None:
            result = result[result[self.STEP_OFFSET_SERIES] < n_examples]

        # re-order rows
        result = result.set_index(gb_series_names, drop=True)
        result = result.sort_index()

        final_result_series = [
            f'{_location_stack.name}_step_{i_step}' for i_step in range(1, steps + 1)
        ]

        if only_converted_paths:
            result = self._filter_navigation_paths_to_conversion(
                result, step_series_name=final_result_series,
            )

        if add_conversion_step_column:
            final_result_series.append(self.CONVERSTION_STEP_COLUMN)

        return result[final_result_series]

    def _generate_navigation_steps(
        self,
        data: bach.DataFrame,
        steps: int,
        by: List[str],
        location_stack: 'SeriesLocationStack',
        start_from_end: bool,
        add_first_conversion_column: bool,
    ) -> bach.DataFrame:
        """
        Generates all steps series and `_first_conversion_step_number` (if required).

        Returns a bach DataFrame including a series for each requested step.
        """
        # adds __feature_nice_name and __root_step_offset to DataFrame
        data = self._prepare_data_for_step_extraction(data, by, location_stack)

        series_to_keep = by + [self.FEATURE_NICE_NAME_SERIES, self.STEP_OFFSET_SERIES]
        if add_first_conversion_column:
            series_to_keep.append('is_conversion_event')

        data = data[series_to_keep]

        data = data.sort_values(by=by + [self.STEP_OFFSET_SERIES], ascending=start_from_end)
        step_window = data.groupby(by=by).window()
        steps_to_add = list(range(1, steps + 1) if not start_from_end else range(steps, 0, -1))

        root_step_series = data[self.FEATURE_NICE_NAME_SERIES]
        root_step_series = root_step_series.copy_override(name=f'{location_stack.name}_step')
        data = self._generate_steps_based_on_series(
            data, step_window, steps_to_add, root_series=root_step_series,
        )

        if add_first_conversion_column:
            data = self._generate_steps_based_on_series(
                data, step_window, steps_to_add, root_series=data['is_conversion_event'],
            )

        data = data.materialize(node_name='step_extraction')

        # remove ending step of entire partition
        if steps > 1:
            if start_from_end:
                mask = data[self.STEP_OFFSET_SERIES] == 0
            else:
                mask = (data[self.STEP_OFFSET_SERIES] != 0) & data[f'{location_stack.name}_step_2'].isnull()
            data = data[~mask]

        if not add_first_conversion_column:
            return data

        return self._calculate_first_conversion_step(data, steps_to_add)

    def _prepare_data_for_step_extraction(
        self,
        data: bach.DataFrame,
        by: List[str],
        location_stack: 'SeriesLocationStack',
    ) -> bach.DataFrame:
        """
        Extracts feature nice name from location stack and calculates the offset of it based
        on the required partitioning and the moment the event happened.

        returns a bach DataFrame including 2 new series: `__feature_nice_name` and `__root_step_offset`.

        .. note::
           This function is internal use only, it expects bach DataFrame contains all required series
           for calculation.
        """
        data = data.copy()

        # adds __feature_nice_name and __root_step_offset to DataFrame
        # extract the nice name per event
        data[self.FEATURE_NICE_NAME_SERIES] = location_stack.ls.nice_name

        # calculate the offset of each nice name

        # always sort by moment, since we need to respect the order of the nice names in the data
        # for getting the correct navigation paths based on event time
        data = data.sort_values(by + ['moment', self.FEATURE_NICE_NAME_SERIES])
        offset_window = data.groupby(by=by).window()
        data[self.STEP_OFFSET_SERIES] = data[location_stack.name].window_row_number(window=offset_window) - 1
        return data.materialize(node_name='pre_step_extraction')

    @staticmethod
    def _generate_steps_based_on_series(
        data: bach.DataFrame,
        step_window: bach.DataFrame,
        steps_to_add: List[int],
        root_series: bach.Series,
    ) -> bach.DataFrame:
        """
        Generates a series for each value in steps_to_add list by getting the offset of the next value
        in `root_series`.

        :param data: bach DataFrame to add new series
        :param step_window: Aggregated bach DataFrame containing the correct partitioning to use
            for getting the sequential values for each step series

        :param steps_to_add: List of sorted integers representing the number of each step to be added.
        :param root_series: bach Series from where to extract the value of each series.

        Example:
             steps_to_add = [1, 2, 3]

             Initial data
             root_series
                 0
                 1
                 2

            Final result
            root_series    root_series_step_1    root_series_step_2     root_series_step_3
                0                0                     1                      2
                1                1                     2                    None
                2                2                   None                   None

        .. note::
        `steps_to_add` param is expected to have a sorted list of integers.
        """
        for idx_step, step in enumerate(steps_to_add):
            # create series for current step based on the offset after the root step
            step_series_name = f'{root_series.name}_{step}'
            if not idx_step:
                data[step_series_name] = root_series.copy()
            else:
                data[step_series_name] = root_series.window_lag(window=step_window, offset=idx_step)

        return data

    def _calculate_first_conversion_step(
        self, data: bach.DataFrame, steps_to_add: List[int],
    ) -> bach.DataFrame:
        """
        Calculates `_first_conversion_step_number` by generating an expression considering all
        `is_conversion_event_{step_number}` series generated by `_generate_navigation_steps` method.

        .. note::
            This function expects that the provided bach DataFrame contains all conversion event step series.
        """
        cols_to_drop = []
        steps_conv_exprs = []
        for step in steps_to_add:
            conv_step_series_name = f'is_conversion_event_{step}'
            cols_to_drop.append(conv_step_series_name)
            steps_conv_exprs.append(
                Expression.construct(
                    f'CASE WHEN {{}} THEN {step}', Expression.identifier(f'is_conversion_event_{step}')
                )
            )

        data[self.CONVERSTION_STEP_COLUMN] = data['is_conversion_event'].copy_override(
            expression=Expression.construct(
                '{}' + ' END' * len(steps_conv_exprs),
                join_expressions(steps_conv_exprs, join_str=' ElSE ')
            ),
        ).copy_override_type(bach.SeriesInt64)

        return data.drop(columns=cols_to_drop)

    def plot_sankey_diagram(
            self,
            steps_df: bach.DataFrame,
            n_top_examples: int = None
    ) -> bach.DataFrame:
        """
        Plot a Sankey Diagram of the Funnel with Plotly.

        This method requires the dataframe from `FunnelDiscovery.get_navigation_paths`: `steps_df`.
        Out of `steps_df` Bach dataframe we construct a new Bach dataframe (in order
        to plot the sankey diagram), which has the following structure:

        - `'source', 'target', 'value'`
        - `'step1', 'step2', 'val1'`
        - `'step2', 'step3', 'val2'`
        - `'...', '...', '...'`

        The navigation steps are our nodes (source and target), the value shows
        how many source -> target links we have.

        :param steps_df: the dataframe which we get from `FunnelDiscovery.get_navigation_paths`.
        :param n_top_examples: number of top examples to plot (if we have
            too many examples to plot it can slow down the browser).

        :returns: Bach DataFrame with `source`, `target` and `value` columns.
        """

        links_df = self._construct_source_target_df(steps_df, n_top_examples)

        links_df_pd = links_df.to_pandas()
        if not links_df_pd.empty:
            # source and target in sankey's diagram must be numeric and not text
            import pandas as pd
            unique_nodes = list(pd.unique(links_df_pd[['source', 'target']].values.ravel()))

            mapping_dict = {k: v for v, k in enumerate(unique_nodes)}
            links_df_pd['source'] = links_df_pd['source'].map(mapping_dict)
            links_df_pd['target'] = links_df_pd['target'].map(mapping_dict)

            links_dict = links_df_pd.to_dict(orient='list')

            import plotly.graph_objects as go
            fig = go.Figure(data=[go.Sankey(
                orientation='h',  # use 'v' for vertical orientation,
                node=dict(
                    pad=25,
                    thickness=15,
                    line=dict(color="black", width=0.5),
                    label=[f'{i[:20]}...' for i in unique_nodes],
                    customdata=unique_nodes,
                    hovertemplate='NODE: %{customdata}',
                ),
                link=dict(
                    source=links_dict["source"],
                    target=links_dict["target"],
                    value=links_dict["value"],
                    customdata=unique_nodes,
                    hovertemplate='SOURCE: %{source.customdata}<br />' +
                                  'TARGET: %{target.customdata}<br />'
                ),
            )])

            fig.update_layout(
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=11,
                ),
                font_color='black',
                title_font_color='black',
                title_text="Location Stack Flow", font_size=14)
            fig.show()
        else:
            print("There is no data to plot.")

        # return all the data without limiting to n_top_examples
        if n_top_examples is not None:
            links_df = self._construct_source_target_df(steps_df)

        return links_df
