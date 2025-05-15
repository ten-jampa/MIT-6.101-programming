'''
6.1010 Spring 23
Lab03 Optional Practice Exercises: Trade Relations
'''

#!/usr/bin/env python3
import os
import pickle
import pytest

import practice

TEST_DIRECTORY = os.path.dirname(__file__)


def setup_module(module):
    """
    This function loads the various databases.  It will be run once every time
    test.py is invoked.
    """
    filename = os.path.join(
        TEST_DIRECTORY,
        'resources',
        'tests',
        f'db_tests.pickle')
    with open(filename, 'rb') as f:
        raw = pickle.load(f)
        for db_name, db in raw['db'].items():
            setattr(module, f'db_{db_name}', db)
        setattr(module, 'test_results', raw)


def compare_lists(x, y, test_name, db_name):
    assert len(x) == len(
        y), f'Failure while testing {test_name} with {db_name} db:\n Expected list of length {len(x)} but got {len(y)}'
    assert isinstance(x, type(
        y)), f'Failure while testing {test_name} with {db_name} db:\n Expected type {type(x)} but got {type(y)}'
    copy = [t for t in x]
    for i, item in enumerate(y):
        assert item in copy, f'Failure while testing {test_name} with {db_name} db:\n Element at index {i}: {item} not found in expected result'
        copy.remove(item)


def compare_sets(x, y, test_name, db_name):
    assert len(x) == len(
        y), f'Failure while testing {test_name} with {db_name} db:\n Expected set of length {len(x)} but got {len(y)}'
    assert isinstance(x, type(
        y)), f'Failure while testing {test_name} with {db_name} db:\n Expected type {type(x)} but got {type(y)}'
    for item in y:
        assert item in x, f'Failure while testing {test_name} with {db_name} db:\n Item {item} not found in expected result'


def compare_dictionary(x, y, test_name, db_name):
    assert len(x) == len(
        y), f'Failure while testing {test_name} with {db_name} db:\n Expected {len(x)} number of keys but got {len(y)}'
    compare_sets(set(x.keys()), set(y.keys()), test_name, db_name)

    for key in y:
        result_values = y[key]
        expected = x[key]
        if isinstance(expected, list):
            try:
                compare_lists(expected, result_values, test_name, db_name)
            except BaseException:
                assert False, f'Failure while testing {test_name} with {db_name} db:\n Expected key {key} to have value {expected} but got {result_values}'
        if isinstance(expected, set):
            try:
                compare_sets(expected, result_values, test_name, db_name)
            except BaseException:
                assert False, f'Failure while testing {test_name} with {db_name} db:\n Expected key {key} to have value {expected} but got {result_values}'


def test_transform_list_pairs():
    test_name = 'list_pairs'
    for db_name, db in test_results['db'].items():
        result = practice.transform_list_pairs(db)
        expected = test_results[test_name][db_name]
        compare_lists(expected, result, test_name, db_name)


def test_transform_set_pairs():
    test_name = 'set_pairs'
    for db_name, db in test_results['db'].items():
        result = practice.transform_set_pairs(db)
        expected = test_results[test_name][db_name]
        compare_sets(expected, result, test_name, db_name)


def test_transform_dict_list():
    test_name = 'dict_list'
    for db_name, db in test_results['db'].items():
        result = practice.transform_dict_list(db)
        expected = test_results[test_name][db_name]
        compare_dictionary(expected, result, test_name, db_name)


def test_transform_dict_set():
    test_name = 'dict_set'
    for db_name, db in test_results['db'].items():
        result = practice.transform_dict_set(db)
        expected = test_results[test_name][db_name]
        compare_dictionary(expected, result, test_name, db_name)


def test_oneway_relations_dict():
    test_name = 'oneway_relations'
    for db_name, db in test_results['db'].items():
        result = practice.oneway_relations_dict(db)
        expected = test_results[test_name][db_name]
        compare_dictionary(expected, result, test_name, db_name)


def test_oneway_loop():
    test_name = 'oneway_loop'
    for db_name, db in test_results['db'].items():
        oneway_relations = test_results['oneway_relations'][db_name]
        for state, expected in test_results[test_name][db_name]:
            result = practice.oneway_loop(db, state)
            assert isinstance(expected, type(
                result)), f'Failure while testing {test_name} with {db_name} db:\n With state {state} expected type {type(expected)} but got {type(result)}'
            if isinstance(expected, list):
                try:
                    compare_lists(expected, result, test_name, db_name)
                except BaseException:
                    assert len(expected) == len(
                        result), f'Failure while testing {test_name} with {db_name} db:\n With state {state} expected path of length {len(expected)} but got {len(result)}'
                    # if the lists are not the same, but the same length, check
                    # that it represents a valid path
                    assert result[0] == expected[
                        0], f'Failure while testing {test_name} with {db_name} db:\n Expected path to start at state {state} but got {result[0]}'
                    assert result[-1] == expected[-1], f'Failure while testing {test_name} with {db_name} db:\n Expected path to end at state {state} but got {result[-1]}'
                    for i in range(len(result) - 1):
                        cur_state = result[i]
                        next_state = result[i + 1]
                        assert next_state in oneway_relations.get(
                            cur_state, []), f'Failure while testing {test_name} with {db_name} db:\n Path found for state {state} is not a valid oneway path {result}'


if __name__ == '__main__':
    import sys
    import json
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--gather", action='store_true')
    parser.add_argument("--server", action='store_true')
    parser.add_argument("--initial", action='store_true')
    parser.add_argument("args", nargs="*")

    parsed = parser.parse_args()

    class TestData:
        def __init__(self, gather=False):
            self.alltests = None
            self.results = {'passed': []}
            self.gather = gather

        @pytest.hookimpl(hookwrapper=True)
        def pytest_runtestloop(self, session):
            yield

        def pytest_runtest_logreport(self, report):
            if report.when != 'call':
                return
            self.results.setdefault(
                report.outcome,
                []).append(
                report.head_line)

        def pytest_collection_finish(self, session):
            if self.gather:
                self.alltests = [i.name for i in session.items]

    pytest_args = ['-v', __file__]

    if parsed.server:
        pytest_args.insert(0, '--color=yes')

    if parsed.gather:
        pytest_args.insert(0, '--collect-only')

    testinfo = TestData(parsed.gather)
    res = pytest.main(
        ['-k', ' or '.join(parsed.args), *pytest_args],
        **{'plugins': [testinfo]}
    )

    if parsed.server:
        _dir = os.path.dirname(__file__)
        if parsed.gather:
            with open(os.path.join(_dir, 'alltests.json'), 'w' if parsed.initial else 'a') as f:
                f.write(json.dumps(testinfo.alltests))
                f.write('\n')
        else:
            with open(os.path.join(_dir, 'results.json'), 'w' if parsed.initial else 'a') as f:
                f.write(json.dumps(testinfo.results))
                f.write('\n')
