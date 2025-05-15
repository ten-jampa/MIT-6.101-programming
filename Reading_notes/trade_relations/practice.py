"""
6.1010 Spring 2023
Lab03 Optional Practice Exercises: Trade Relations
"""

import csv

# no additional imports allowed


def transform_list_pairs(database):
    """
    Transforms the database into a more concise format that only includes
    transactions where the origin is different from the destination.

    Parameters:
        * database (list) : a list where each element is a list of the form
            [
             origin_state (str),
             destination_state (str),
             item (str),
             transportation (str),
             value (int)
            ]

    Returns:
        A list where each element is a list of the form
            [origin_state (str), destination_state (str)].
    """
    raise NotImplementedError


def transform_set_pairs(database):
    """
    Transforms the database into a more concise set that only includes
    transactions where the origin is different from the destination.

    Parameters:
        * database (list) : a list where each element is a list of the form
            [
             origin_state (str),
             destination_state (str),
             item (str),
             transportation (str),
             value (int),
            ]

    Returns:
        A set where each element is a tuple of the form
            (origin_state (str), destination_state (str)).
    """
    raise NotImplementedError


def transform_dict_list(database):
    """
    Transforms the database into a dictionary mapping origin_states to a
    list of destination states. Only includes transactions where the origin
    is different from the destination (note destinations may be repeated.)
    Only includes origin states with at least one destination.

    Parameters:
        * database (list) : a list where each element is a list of the form
            [
             origin_state (str),
             destination_state (str),
             item (str),
             transportation (str),
             value (int),
            ]

    Returns:
        A dictionary with keys that are origin_states and values that are a
        list of strings of all destination states.
            {origin_state (str) : [destination_state (str), ...]}
    """
    raise NotImplementedError


def transform_dict_set(database):
    """
    Transforms the database into a dictionary mapping origin_states to a
    list of destination states. Only includes transactions where the origin
    is different from the destination. Only includes origin states with at least
    one destination.

    Parameters:
        * database (list) : a list where each element is a list of the form
            [
             origin_state (str),
             destination_state (str),
             item (str),
             transportation (str),
             value (int),
            ]

    Returns:
        A dictionary with keys that are origin_states and values that are a
        set of strings of all destination states.
            {origin_state (str) : {destination_state (str), ...}}
    """
    raise NotImplementedError


def oneway_relations_dict(database):
    """
    Create dictionary representing only the oneway trade relationships
    in the database. A oneway trade relationship is defined as a pair of
    states where state A shipped products to state B, but state B never
    shipped anything to state A. Only states with at least one oneway trade
    relationship should be included.

    Parameters:
        * database (list) : a list where each element is a list of the form
            [
             origin_state (str),
             destination_state (str),
             item (str),
             transportation (str),
             value (int),
            ]

    Returns:
        A dictionary with keys that are origin_states and values that are a
        set of strings of all oneway destination states.
            {origin_state (str) : {destination_state (str), ...}}
    """
    raise NotImplementedError


def oneway_loop(database, state):
    """
    Finds a path representing the smallest number of states with oneway trade
    relationships that form a loop starting and ending with the given state.

    Parameters:
        * database (list) : a list where each element is a list of the form
            [
             origin_state (str),
             destination_state (str),
             item (str),
             transportation (str),
             value (int),
            ]
        * state (str) : the desired start and end state

    Returns:
        A list of state strings representing the path, or None if there is no such path.

    Notes:
        * In the tiny DB, the shortest oneway loop for ND would be
          [ND, SC, MT, ND]. [ND, SC, MT, WY, ND] is a valid oneway loop but not
          the shortest loop.
        * In the tiny DB, there is no oneway loop for MA so it should return
        None.
    """
    raise NotImplementedError


def load_database(filename):
    """
    Reads the database from the given CSV file and processes it into a list of
    lists.

    Parameters:
        * filename (str) : database file to be read

    Returns:
        * database (list) : a list where each element is a list of the form
            [
             origin_state (str),
             destination_state (str),
             item (str),
             transportation (str),
             value (int),
            ]
    """
    with open(filename, "r", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        next(csv_reader)  # skip header
        database = []
        for entry in csv_reader:
            database.append(entry)
            database[-1][-1] = int(entry[-1])  # change amounts to integers
    return database


if __name__ == "__main__":
    # These are the same databases used in the test.py file:

    tiny_database = load_database("resources/tiny_transactions.csv")
    large_database = load_database("resources/large_transactions.csv")
    small_database = large_database[:20]
    medium_database = large_database[:1000]

    ########################################################################
    # Your code below:

    for row in tiny_database:
        print(row)
