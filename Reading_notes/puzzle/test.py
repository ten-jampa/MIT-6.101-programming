"""
6.1010 Spring 2023
Lab04 Optional Practice Exercises: Puzzle
"""

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
        "resources",
        "puzzle_tests.pickle")
    with open(filename, "rb") as f:
        raw = pickle.load(f)
        setattr(module, "test_results", raw)

def blist(board):
    return [list(row) for row in board]

def str_board(board):
    """
    Given a board, print it out in aligned rows.
    """
    result = ''
    for row in board:
        result +=f"{'  '.join([' '+str(num) if num is not None and num < 10 else str(num) if num is not None else ' X' for num in row]):25}\n"
    return result

def test_find_blank_loc_15():
    key = 'big_moves_extra_large'
    for test_name, blank_boards in test_results.items():
        if key in test_name:
            for exp_loc, board in blank_boards:
                b = blist(board)
                b_og = blist(board)
                result = practice.find_blank(b)
                assert b_og == b, "Remember to not mutate the board!"
                err_msg = f'{result} != exp {exp_loc} for board \n {str_board(board)}'
                assert result == exp_loc, err_msg

def test_find_blank_loc_8():
    key = 'small_moves_extra_large'
    for test_name, blank_boards in test_results.items():
        if key in test_name:
            for exp_loc, board in blank_boards:
                b = blist(board)
                b_og = blist(board)
                result = practice.find_blank(b)
                assert b_og == b, "Remember to not mutate the board!"
                err_msg = f'{result} != exp {exp_loc} for board \n {str_board(board)}'
                assert result == exp_loc, err_msg
                
def test_find_blank_loc_rect():
    key = 'rect_moves_extra_large'
    for test_name, blank_boards in test_results.items():
        if key in test_name:
            for exp_loc, board in blank_boards:
                b = blist(board)
                b_og = blist(board)
                result = practice.find_blank(b)
                assert b_og == b, "Remember to not mutate the board!"
                err_msg = f'{result} != exp {exp_loc} for board \n {str_board(board)}'
                assert result == exp_loc, err_msg

def compare_paths(result_path, expected_path, test_name):
    assert bool(result_path),  f'{test_name} expected path list of length {len(expected_path)} but got {result_path}'
    assert len(result_path) == len(expected_path), \
        f'{test_name} expected path length {len(expected_path)} but got {len(result_path)}'
    for i, (rboard, eboard) in enumerate(zip(result_path, expected_path)):
        err_msg = f'{test_name} boards at move {i} do not match!\n exp:\n {str_board(eboard)} \n result:\n{str_board(rboard)}'
        assert blist(rboard) == blist(eboard), err_msg

def test_solve_tiny_15():
    key = 'big_moves_tiny_solve'
    for test_name, exp_path in test_results.items():
        if key in test_name:
            inp = blist(exp_path[0]) 
            result = practice.solve_puzzle(inp)
            compare_paths(result, exp_path, test_name)

def test_solve_tiny_8():
    key = 'small_moves_tiny_solve'
    for test_name, exp_path in test_results.items():
        if key in test_name:
            inp = blist(exp_path[0]) 
            result = practice.solve_puzzle(inp)
            compare_paths(result, exp_path, test_name)

def test_solve_tiny_rect():
    key = 'rect_moves_tiny_solve'
    for test_name, exp_path in test_results.items():
        if key in test_name:
            inp = blist(exp_path[0]) 
            result = practice.solve_puzzle(inp)
            compare_paths(result, exp_path, test_name)

def test_solve_medium():
    for shape in ['rect', 'small', 'large']:
        key = f'{shape}_moves_medium_solve'
        for test_name, exp_path in test_results.items():
            if key in test_name:
                inp = blist(exp_path[0]) 
                result = practice.solve_puzzle(inp)
                compare_paths(result, exp_path, test_name)

def test_solve_large():
    for shape in ['rect', 'small', 'large']:
        key = f'{shape}_moves_large_solve'
        for test_name, exp_path in test_results.items():
            if key in test_name:
                inp = blist(exp_path[0]) 
                result = practice.solve_puzzle(inp)
                compare_paths(result, exp_path, test_name)

if __name__ == "__main__":
    import sys
    import json
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--gather", action="store_true")
    parser.add_argument("--server", action="store_true")
    parser.add_argument("--initial", action="store_true")
    parser.add_argument("args", nargs="*")

    parsed = parser.parse_args()

    class TestData:
        def __init__(self, gather=False):
            self.alltests = None
            self.results = {"passed": []}
            self.gather = gather

        @pytest.hookimpl(hookwrapper=True)
        def pytest_runtestloop(self, session):
            yield

        def pytest_runtest_logreport(self, report):
            if report.when != "call":
                return
            self.results.setdefault(
                report.outcome,
                []).append(
                report.head_line)

        def pytest_collection_finish(self, session):
            if self.gather:
                self.alltests = [i.name for i in session.items]

    pytest_args = ["-v", __file__]

    if parsed.server:
        pytest_args.insert(0, "--color=yes")

    if parsed.gather:
        pytest_args.insert(0, "--collect-only")

    testinfo = TestData(parsed.gather)
    res = pytest.main(["-k", " or ".join(parsed.args), *
                       pytest_args], **{"plugins": [testinfo]})

    if parsed.server:
        _dir = os.path.dirname(__file__)
        if parsed.gather:
            with open(
                os.path.join(_dir, "alltests.json"), "w" if parsed.initial else "a"
            ) as f:
                f.write(json.dumps(testinfo.alltests))
                f.write("\n")
        else:
            with open(
                os.path.join(_dir, "results.json"), "w" if parsed.initial else "a"
            ) as f:
                f.write(json.dumps(testinfo.results))
                f.write("\n")
