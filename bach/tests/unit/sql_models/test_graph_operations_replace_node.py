"""
Copyright 2021 Objectiv B.V.

Tests for the replace_node_in_graph() function in sql_models.generic.graph_operations
There are a lot of cases to consider for that function, that's why this file has been split of from
    test_graph_operations.py
"""
import pytest

from sql_models.graph_operations import get_node, replace_node_in_graph, get_graph_nodes_info, \
    replace_non_start_node_in_graph
from sql_models.model import SqlModel, RefPath
from tests.unit.sql_models.util import ValueModel, RefModel, JoinModel, RefValueModel


pytestmark = [pytest.mark.db_independent]  # mark all tests here as database independent.


def call_replace_node_in_graph(
        start_node: SqlModel,
        reference_path: RefPath,
        replacement_model: SqlModel) -> SqlModel:
    """
    Helper, calls both replace_node_in_graph() and replace_non_start_node_in_graph() and returns the result.
    Additional makes sure that:
        1) both functions give the same output (if reference_path != tuple())
        2) replace_non_start_node_in_graph() raises an exception if reference_path is an empty tuple
        3) replace_non_start_node_in_graph() returns the same type as start_node
    """
    result1 = replace_node_in_graph(start_node, reference_path, replacement_model)
    if reference_path == tuple():
        with pytest.raises(ValueError, match='reference path cannot be empty'):
            replace_non_start_node_in_graph(start_node, reference_path, replacement_model)
        return result1
    result2 = replace_non_start_node_in_graph(start_node, reference_path, replacement_model)
    assert result1 == result2
    assert result1.hash == result2.hash  # should be implied by the previous, but let's double check
    assert type(result2) == type(start_node)
    return result1


def test_replace_node_in_graph_trivial():
    # One node graph
    graph1 = ValueModel.build(key='a', val=1)
    replacement_node1 = ValueModel.build(key='b', val=99)
    new_graph1 = call_replace_node_in_graph(graph1, tuple(), replacement_node1)
    assert graph1.placeholders['val'] == 1
    assert new_graph1.placeholders['val'] == 99
    assert graph1.hash != new_graph1.hash

    # Four node graph. replace first node
    vm1 = ValueModel.build(key='a', val=1)
    vm2 = ValueModel.build(key='a', val=2)
    rm = RefModel.build(ref=vm1)
    graph2 = JoinModel.build(ref_left=rm, ref_right=vm2)
    replacement_node2 = ValueModel.build(key='b', val=99)
    new_graph2 = call_replace_node_in_graph(graph2, tuple(), replacement_node2)
    assert graph2.placeholders == {}
    assert len(graph2.references) == 2
    assert new_graph2.placeholders['val'] == 99
    assert len(new_graph2.references) == 0
    assert graph2.hash != new_graph2.hash


def test_replace_node_in_graph_simple():
    # Graph:
    #   vm2 <---------\
    #                  +-- graph
    #   vm1 <-- rm <--/
    #
    vm1 = ValueModel.build(key='a', val=1)
    vm2 = ValueModel.build(key='a', val=2)
    rm = RefModel.build(ref=vm1)
    graph = JoinModel.build(ref_left=rm, ref_right=vm2)

    replacement_node = ValueModel.build(key='b', val=99)

    new_graph = call_replace_node_in_graph(graph, ('ref_left', 'ref'), replacement_node)
    assert get_node(graph, ('ref_left', 'ref')).placeholders['val'] == 1
    assert get_node(new_graph, ('ref_left', 'ref')).placeholders['val'] == 99
    assert graph.hash != new_graph.hash


def test_replace_node_in_graph_simple_duplicate_paths():
    # simple graph in which there are two paths to vm1
    # Graph:
    #          /---------\
    #          |          +-- graph
    #   vm1 <--+-- rm <--/
    #
    vm1 = ValueModel.build(key='a', val=1)
    rm = RefModel.build(ref=vm1)
    graph = JoinModel.build(ref_left=rm, ref_right=vm1)

    replacement_node = ValueModel.build(key='b', val=99)

    # build two new graphs: use both reference paths
    new_graph1 = call_replace_node_in_graph(graph, ('ref_left', 'ref'), replacement_node)
    new_graph2 = call_replace_node_in_graph(graph, ('ref_right',), replacement_node)

    info = get_graph_nodes_info(graph)
    new_info = get_graph_nodes_info(new_graph1)

    assert len(info) == 3
    assert get_node(graph, ('ref_left', 'ref')) is get_node(graph, ('ref_right',))
    assert get_node(graph, ('ref_left', 'ref')).placeholders['val'] == 1
    assert get_node(graph, ('ref_right',)).placeholders['val'] == 1

    assert len(new_info) == 3  # The node that is referenced twice should be replace by a single node again
    assert get_node(new_graph1, ('ref_left', 'ref')).placeholders['val'] == 99
    assert get_node(new_graph1, ('ref_right',)).placeholders['val'] == 99
    assert get_node(new_graph1, ('ref_left', 'ref')).hash == get_node(new_graph1, ('ref_right',)).hash
    assert get_node(new_graph1, ('ref_left', 'ref')) is get_node(new_graph1, ('ref_right',))
    assert graph.hash != new_graph1.hash

    # Assert that the alternative new graph, built using the other reference path has the same structure
    #  and data, but is a different copy
    assert new_graph1 is not new_graph2
    assert len(get_graph_nodes_info(new_graph2)) == 3
    assert new_graph1.hash == new_graph2.hash


def test_replace_node_in_graph_duplicate_paths2():
    # graph in which there are two paths to vm1, and there are nodes in common in both paths at the tail of
    #   the paths
    #
    # Graph:
    #                  /-- rm3 <--\
    #   vm1 <-- rm1 <--+           +-- graph
    #                  \-- rm2 <--/
    #
    vm1 = ValueModel.build(key='a', val=1)
    rm1 = RefModel.build(ref=vm1)
    rm2 = RefModel.build(ref=rm1)
    rm3 = RefModel.build(ref=rm1)
    graph = JoinModel.build(ref_left=rm2, ref_right=rm3)

    replacement_node = ValueModel.build(key='b', val=99)
    # build two new graphs: use both reference paths
    new_graph1 = call_replace_node_in_graph(graph, ('ref_left', 'ref', 'ref'), replacement_node)
    new_graph2 = call_replace_node_in_graph(graph, ('ref_right', 'ref', 'ref'), replacement_node)
    info = get_graph_nodes_info(graph)
    new_info = get_graph_nodes_info(new_graph1)

    assert len(info) == 5
    # two paths to same node
    assert get_node(graph, ('ref_left', 'ref', 'ref')) is get_node(graph, ('ref_right', 'ref', 'ref'))
    assert get_node(graph, ('ref_left', 'ref', 'ref')).placeholders['val'] == 1
    assert get_node(graph, ('ref_right', 'ref', 'ref')).placeholders['val'] == 1

    assert len(new_info) == 5  # All nodes should be replaced one on one with new nodes
    new_node_left = get_node(new_graph1, ('ref_left', 'ref', 'ref'))
    new_node_right = get_node(new_graph1, ('ref_right', 'ref', 'ref'))
    assert new_node_left.placeholders['val'] == 99
    assert new_node_right.placeholders['val'] == 99
    assert new_node_left.hash == new_node_right.hash
    assert new_node_left is new_node_right
    assert graph.hash != new_graph1.hash

    # Assert that the alternative new graph, built using the other reference path has the same structure
    #  and data, but is a different copy
    assert new_graph1 is not new_graph2
    assert len(get_graph_nodes_info(new_graph2)) == 5
    assert new_graph1.hash == new_graph2.hash


def test_replace_node_in_graph_non_leaf_node():
    #
    # Graph:
    #                                     /-- rm3 <--\
    #   vm1 <-- rvm1 <-- rvm2 <-- rm1 <--+           +-- graph
    #                                     \-- rm2 <--/
    #
    # Replacement node: rvm2
    #
    vm1 = ValueModel.build(key='a', val=1)
    rvm1 = RefValueModel.build(ref=vm1, val=5)
    rvm2 = RefValueModel.build(ref=rvm1, val=10)
    rm1 = RefModel.build(ref=rvm2)
    rm2 = RefModel.build(ref=rm1)
    rm3 = RefModel.build(ref=rm1)
    graph = JoinModel.build(ref_left=rm2, ref_right=rm3)

    replacement_node = RefValueModel.build(ref=rvm1, val=1337)
    new_graph1 = call_replace_node_in_graph(graph, ('ref_left', 'ref', 'ref'), replacement_node)
    new_graph2 = call_replace_node_in_graph(graph, ('ref_right', 'ref', 'ref'), replacement_node)
    info = get_graph_nodes_info(graph)
    new_info = get_graph_nodes_info(new_graph1)

    assert len(info) == 7
    # two paths to node that we replace.
    # Check that both nodes are the same, have the same values, and same tail node
    node_left = get_node(graph, ('ref_left', 'ref', 'ref'))
    node_right = get_node(graph, ('ref_right', 'ref', 'ref'))
    assert node_left is node_right
    assert node_left.placeholders['val'] == 10
    assert node_right.placeholders['val'] == 10
    assert get_node(node_left, ('ref', )) is get_node(node_right, ('ref', ))

    assert len(new_info) == 7  # Number of nodes shouldn't change
    new_node_left = get_node(new_graph1, ('ref_left', 'ref', 'ref'))
    new_node_right = get_node(new_graph1, ('ref_right', 'ref', 'ref'))
    assert new_node_left.placeholders['val'] == 1337
    assert new_node_right.placeholders['val'] == 1337
    assert new_node_left.hash == new_node_right.hash
    assert new_node_left is new_node_right
    assert get_node(new_node_left, ('ref',)) is get_node(new_node_right, ('ref',))
    assert graph.hash != new_graph1.hash

    # Assert that the alternative new graph, built using the other reference path has the same structure
    #  and data, but is a different copy
    assert new_graph1 is not new_graph2
    assert len(get_graph_nodes_info(new_graph2)) == 7
    assert new_graph1.hash == new_graph2.hash


def test_replace_node_in_graph_complex1():
    # See also test_replace_node_in_graph_complex2, which uses the same graph but replace a different node
    #
    # Graph:
    #                                         /-- rm2 <--\
    #   vm1 <-- rvm1 <--+--- rvm2 <-- rm1 <--+           +-- graph
    #                    \                    \-- jm2 <--/
    #                     \                       /
    #                      +-- jm1 <-------------/
    #                     /
    #            vm2 <---/
    #
    # Replacement node1: rvm2
    #
    vm1 = ValueModel.build(key='a', val=1)
    rvm1 = RefValueModel.build(ref=vm1, val=5)
    rvm2 = RefValueModel.build(ref=rvm1, val=10)
    rm1 = RefModel.build(ref=rvm2)
    rm2 = RefModel.build(ref=rm1)
    vm2 = ValueModel.build(key='a', val=2)
    jm1 = JoinModel.build(ref_left=vm2, ref_right=rvm1)
    jm2 = JoinModel.build(ref_left=jm1, ref_right=rm1)
    graph = JoinModel.build(ref_left=jm2, ref_right=rm2)

    replacement_node = RefValueModel.build(ref=rvm1, val=1337)
    new_graph1 = call_replace_node_in_graph(graph, ('ref_right', 'ref', 'ref'), replacement_node)
    new_graph2 = call_replace_node_in_graph(graph, ('ref_left', 'ref_right', 'ref'), replacement_node)
    info = get_graph_nodes_info(graph)
    new_info = get_graph_nodes_info(new_graph1)

    assert len(info) == 9
    # two paths to node that we replace.
    # Check that both nodes are the same, have the same values, and same tail node
    node_left = get_node(graph, ('ref_right', 'ref', 'ref'))
    node_right = get_node(graph, ('ref_left', 'ref_right', 'ref'))
    assert node_left is node_right
    assert node_left.placeholders['val'] == 10
    assert node_right.placeholders['val'] == 10
    assert get_node(node_left, ('ref', )) is get_node(node_right, ('ref', ))

    assert len(new_info) == 9  # Number of nodes shouldn't change
    new_node_left = get_node(new_graph1, ('ref_right', 'ref', 'ref'))
    new_node_right = get_node(new_graph1, ('ref_left', 'ref_right', 'ref'))
    assert new_node_left.placeholders['val'] == 1337
    assert new_node_right.placeholders['val'] == 1337
    assert new_node_left.hash == new_node_right.hash
    assert new_node_left is new_node_right
    assert get_node(new_node_left, ('ref',)) is get_node(new_node_right, ('ref',))
    assert graph.hash != new_graph1.hash

    # Assert that the alternative new graph, built using the other reference path has the same structure
    #  and data, but is a different copy
    assert new_graph1 is not new_graph2
    assert len(get_graph_nodes_info(new_graph2)) == 9
    assert new_graph1.hash == new_graph2.hash
    # The nodes that are changed in both graph should be different instances
    assert get_node(new_graph1, ('ref_left',)) is not get_node(new_graph2, ('ref_left',))
    # The nodes that are un-changed in both graphs should be the same instances
    assert get_node(new_graph1, ('ref_left', 'ref_left')) is get_node(new_graph2, ('ref_left', 'ref_left'))


def test_replace_node_in_graph_complex2():
    # See also test_replace_node_in_graph_complex1, which uses the same graph but replace a different node
    #
    # Graph:
    #                                         /-- rm2 <--\
    #   vm1 <-- rvm1 <--+--- rvm2 <-- rm1 <--+           +-- graph
    #                    \                    \-- jm2 <--/
    #                     \                       /
    #                      +-- jm1 <-------------/
    #                     /
    #            vm2 <---/
    #
    # Replacement node1: rvm1
    #
    vm1 = ValueModel.build(key='a', val=1)
    rvm1 = RefValueModel.build(ref=vm1, val=5)
    rvm2 = RefValueModel.build(ref=rvm1, val=10)
    rm1 = RefModel.build(ref=rvm2)
    rm2 = RefModel.build(ref=rm1)
    vm2 = ValueModel.build(key='a', val=2)
    jm1 = JoinModel.build(ref_left=vm2, ref_right=rvm1)
    jm2 = JoinModel.build(ref_left=jm1, ref_right=rm1)
    graph = JoinModel.build(ref_left=jm2, ref_right=rm2)

    replacement_node = RefValueModel.build(ref=vm1, val=1337)
    new_graph1 = call_replace_node_in_graph(graph, ('ref_right', 'ref', 'ref', 'ref'), replacement_node)
    new_graph2 = call_replace_node_in_graph(graph, ('ref_left', 'ref_right', 'ref', 'ref'), replacement_node)
    new_graph3 = call_replace_node_in_graph(graph, ('ref_left', 'ref_left', 'ref_right'), replacement_node)
    info = get_graph_nodes_info(graph)
    new_info = get_graph_nodes_info(new_graph1)

    assert len(info) == 9
    # two paths to node that we replace.
    # Check that both nodes are the same, have the same values, and same tail node
    node_one = get_node(graph, ('ref_right', 'ref', 'ref', 'ref'))
    node_two = get_node(graph, ('ref_left', 'ref_right', 'ref', 'ref'))
    node_three = get_node(graph, ('ref_left', 'ref_left', 'ref_right'))
    assert node_one is node_two
    assert node_one is node_three
    assert node_one.placeholders['val'] == 5
    assert node_two.placeholders['val'] == 5
    assert node_three.placeholders['val'] == 5
    assert get_node(node_one, ('ref',)) is get_node(node_two, ('ref', ))
    assert get_node(node_one, ('ref',)) is get_node(node_three, ('ref',))

    assert len(new_info) == 9  # Number of nodes shouldn't change
    new_node_one = get_node(new_graph1, ('ref_right', 'ref', 'ref', 'ref'))
    new_node_two = get_node(new_graph1, ('ref_left', 'ref_right', 'ref', 'ref'))
    new_node_three = get_node(new_graph1, ('ref_left', 'ref_left', 'ref_right'))
    assert new_node_one is new_node_two
    assert new_node_one is new_node_three
    assert new_node_one.placeholders['val'] == 1337
    assert new_node_two.placeholders['val'] == 1337
    assert new_node_three.placeholders['val'] == 1337
    assert get_node(new_node_one, ('ref',)) is get_node(new_node_two, ('ref', ))
    assert get_node(new_node_one, ('ref',)) is get_node(new_node_three, ('ref',))
    assert graph.hash != new_graph1.hash

    # Assert that the alternative new graphs, built using the other reference paths have the same structure
    #  and data, but are different copies
    assert new_graph1 is not new_graph2
    assert new_graph1 is not new_graph3
    assert new_graph2 is not new_graph3
    assert len(get_graph_nodes_info(new_graph2)) == 9
    assert len(get_graph_nodes_info(new_graph3)) == 9
    assert new_graph1.hash == new_graph2.hash == new_graph3.hash
    # The nodes that are changed in the graphs should be different instances
    assert get_node(new_graph1, ('ref_left',)) is not get_node(new_graph2, ('ref_left',))
    assert get_node(new_graph1, ('ref_left',)) is not get_node(new_graph3, ('ref_left',))
    assert get_node(new_graph2, ('ref_left',)) is not get_node(new_graph3, ('ref_left',))
    # The nodes that are un-changed in the graphs should be the same instances in all three graphs
    assert get_node(new_graph1, ('ref_left', 'ref_left', 'ref_left')) is \
           get_node(new_graph2, ('ref_left', 'ref_left', 'ref_left'))
    assert get_node(new_graph1, ('ref_left', 'ref_left', 'ref_left')) is \
           get_node(new_graph3, ('ref_left', 'ref_left', 'ref_left'))
    assert get_node(new_graph2, ('ref_left', 'ref_left', 'ref_left')) is \
           get_node(new_graph3, ('ref_left', 'ref_left', 'ref_left'))
