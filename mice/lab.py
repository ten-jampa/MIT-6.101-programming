#!/usr/bin/env python3
"""
6.101 Lab:
Mice-sleeper
"""

# import typing  # optional import
# import pprint  # optional import
import doctest

# NO ADDITIONAL IMPORTS ALLOWED!


def dump(game, all_keys=False):
    """
    Prints a human-readable version of a game (provided as a dictionary)

    By default uses only "board", "dimensions", "state", "visible" keys (used
    by doctests). Setting all_keys=True shows all game keys.
    """
    if all_keys:
        keys = sorted(game)
    else:
        keys = ("board", "dimensions", "state", "visible")
        # Use only default game keys. If you modify this you will need
        # to update the docstrings in other functions!

    for key in keys:
        val = game[key]
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f"{key}:")
            for inner in val:
                print(f"    {inner}")
        else:
            print(f"{key}:", val)


# 2-D IMPLEMENTATION


def neighbouring_cells_2d(irow, icol, dimensions):
    """2-dimensional version to get the neighbouring cells
    around the specified cell coordinate of irow, icol
    """
    return get_adjacents_nd(dimensions, (irow, icol))


def new_game_2d(nrows, ncolumns, mice):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Parameters:
       nrows (int): Number of rows
       ncolumns (int): Number of columns
       mice (list): List of mouse locations as (row, column) tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['m', 3, 1, 0]
        ['m', 'm', 1, 0]
    dimensions: (2, 4)
    state: ongoing
    visible:
        [False, False, False, False]
        [False, False, False, False]
    """
    return new_game_nd((nrows, ncolumns), mice)


def win_check_2d(game):
    """Helper function that checks if the game has been won and if so, changes
    the state of the game to 'won'
    """
    win_check_nd(game)


def reveal_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['visible'] to reveal (row, col).  Then, if (row, col) has no
    adjacent mice (including diagonally), then recursively reveal its eight
    neighbors.  Return an integer indicating how many new squares were revealed
    in total, including neighbors, and neighbors of neighbors, and so on.

    The state of the game should be changed to 'lost' when at least one mouse
    is visible on the board, 'won' when all safe squares (squares that do not
    contain a mouse) and no mice are visible, and 'ongoing' otherwise.

    If the game is not ongoing, or if the given square has already been
    revealed, reveal_2d should not reveal any squares.

    Parameters:
       game (dict): Game state
       row (int): Where to start revealing cells (row)
       col (int): Where to start revealing cells (col)

    Returns:
       int: the number of new squares revealed

    >>> game = new_game_2d(2, 4, [(0,0), (1, 0), (1, 1)])
    >>> reveal_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['m', 3, 1, 0]
        ['m', 'm', 1, 0]
    dimensions: (2, 4)
    state: ongoing
    visible:
        [False, False, True, True]
        [False, False, True, True]
    >>> reveal_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['m', 3, 1, 0]
        ['m', 'm', 1, 0]
    dimensions: (2, 4)
    state: lost
    visible:
        [True, False, True, True]
        [False, False, True, True]
    """
    return reveal_nd(game, (row, col))


def render_2d(game, all_visible=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    'm' (mice), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    mice).  game['visible'] indicates which squares should be visible.  If
    all_visible is True (the default is False), game['visible'] is ignored and
    all cells are shown.

    Parameters:
       game (dict): Game state
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                    by game['visible']

    Returns:
       A 2D array (list of lists)

    >>> game = new_game_2d(2, 4, [(0,0), (1, 0), (1, 1)])
    >>> render_2d(game, False)
    [['_', '_', '_', '_'], ['_', '_', '_', '_']]
    >>> render_2d(game, True)
    [['m', '3', '1', ' '], ['m', 'm', '1', ' ']]
    >>> reveal_2d(game, 0, 3)
    4
    >>> render_2d(game, False)
    [['_', '_', '1', ' '], ['_', '_', '1', ' ']]
    """
    return render_nd(game, all_visible)


# N-D IMPLEMENTATION


def create_n_dim_list(dimensions, value=0):
    """
    A recursive function to create an N-dimensional grid
    """
    # if render:
    #     #you are using this list to render things
    if len(dimensions) == 0:
        return value
    return [create_n_dim_list(dimensions[1:], value) for _ in range(dimensions[0])]


def set_value_on_board_nd(board, coordinates, value, add=False):
    """
    Set the value at a specific coordinate in an N-dimensional list.
    """
    if isinstance(coordinates, int):
        coordinates = (coordinates,)

    if add:
        if len(coordinates) == 1:
            if board[coordinates[0]] != "m":
                new_val = board[coordinates[0]] + value
                board[coordinates[0]] = max(new_val, 0)
        else:
            set_value_on_board_nd(
                board[coordinates[0]], coordinates[1:], value, add=True
            )
    else:
        # we are setting values
        if len(coordinates) == 1:
            board[coordinates[0]] = value  # regardless of what has been put down
        else:
            set_value_on_board_nd(
                board[coordinates[0]], coordinates[1:], value, add=False
            )


def get_all_coord(dimension):
    """Recursive function to retrieve all the coordinates for an n-dimensional grid"""
    # assuming dimension is a tuple at least
    out = []
    # base case:
    if len(dimension) == 1:
        return range(dimension[0])
    first_dim, rest_dim = dimension[0], dimension[1:]

    for ix in range(first_dim):
        for irest in get_all_coord(rest_dim):
            if isinstance(irest, tuple):
                _coordinate_ = (ix,) + irest
                out.append(_coordinate_)
            else:
                _coordinate_ = (ix, irest)
                out.append(_coordinate_)
    return out


def get_adjacents_nd(dimension, coordinate):
    """Recursive function to get all the adjacent coordinates for a given coordinate
    in a given n-dimensional grid"""
    if isinstance(coordinate, int):
        coordinate = (coordinate,)
    if isinstance(dimension, int):
        dimension = (dimension,)

    # Base case:
    if len(coordinate) == 1 and len(dimension) == 1:
        return tuple(
            range(max(coordinate[0] - 1, 0), min(coordinate[0] + 2, dimension[0]))
        )

    # Recursive case:
    first_dimen, rest_dimen = dimension[0], dimension[1:]
    first_coord, rest_coord = coordinate[0], coordinate[1:]
    adjacent_coordinates = []
    for adj_f_coord in range(
        max(first_coord - 1, 0), min(first_coord + 2, first_dimen)
    ):
        # print(f'First coordinate {adj_f_coord}')
        for adj_s_coord in get_adjacents_nd(rest_dimen, rest_coord):
            # print(f'Second coordinate {adj_s_coord}')
            if isinstance(adj_s_coord, tuple):
                adj_coordinate = (adj_f_coord,) + adj_s_coord
                adjacent_coordinates.append(adj_coordinate)
            else:
                adj_coordinate = (adj_f_coord, adj_s_coord)
                adjacent_coordinates.append(adj_coordinate)
    return adjacent_coordinates


def retrieve_val_nd(board, coordinate):
    """Helper function to retrieve the value at the given coordinate value
    for the n-dimensional board
    """
    if isinstance(coordinate, int):
        coordinate = (coordinate,)

    # Base case
    if len(coordinate) == 1:
        return board[coordinate[0]]
    # Recursive case
    return retrieve_val_nd(board[coordinate[0]], coordinate[1:])


def new_game_nd(dimensions, mice):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Parameters:
       dimensions (tuple): Dimensions of the board
       mice (list): mouse locations as a list of tuples, each an
                    N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, 'm'], [3, 3], [1, 1], [0, 0]]
        [['m', 3], [3, 'm'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """

    board = create_n_dim_list(dimensions, 0)
    visible = create_n_dim_list(dimensions, False)
    bed_board = create_n_dim_list(dimensions, False)
    mice_set = set(mice)
    # first add mice
    for mice_coordinate in mice_set:
        set_value_on_board_nd(board, mice_coordinate, "m")
        neighbor_coordinates = get_adjacents_nd(dimensions, mice_coordinate)
        for neighbour_coordinate in neighbor_coordinates:
            if neighbour_coordinate in mice_set:
                continue
            else:
                set_value_on_board_nd(board, neighbour_coordinate, 1, add=True)

    safe_squares = count_safe_squares(board)
    return {
        "dimensions": dimensions,
        "board": board,
        "state": "ongoing",
        "visible": visible,
        "mice": mice_set,
        "bed_board": bed_board,
        "safe_squares": safe_squares,
        "first_turn": True,
    }


def count_safe_squares(board):
    """Given a board, count all the safe squares, that is
    the squares that don't have mice"""
    if isinstance(board[0], list):
        return sum(count_safe_squares(sub_board) for sub_board in board)
    return sum(val != "m" for val in board)  # a single line grid


def count_revealed_squares(visible):
    """Given the visible board, count all the squares that have
    been revealed."""
    if isinstance(visible[0], list):
        return sum(count_revealed_squares(sub_visible) for sub_visible in visible)
    return sum(visible)  # a single line grid


def win_check_nd(game):
    """Helper function that checks if the n-dimensional
    game has been won and if so, changes
    the state of the game to 'won'
    """
    if game["state"] != "ongoing":
        return

    safe_squares = game["safe_squares"]
    revealed_squares = count_revealed_squares(game["visible"])
    if revealed_squares == safe_squares:
        # print('You have won the game!')
        game["state"] = "won"


def move_(game, coordinates):
    """Function that takes in a game and
    moves the mices in the coordinate list to other
    squares"""

    dimensions = game["dimensions"]
    mice_set = game["mice"]
    adj_coords = set(get_adjacents_nd(dimensions, coordinates))

    # we prepare the new board
    new_board = create_n_dim_list(dimensions, 0)
    for mice in mice_set:
        set_value_on_board_nd(new_board, mice, "m")

    def good_new_coordinate(old_coordinates_list, new_coordinate):
        if new_coordinate in old_coordinates_list:
            return False
        if new_coordinate in mice_set:
            return False
        else:
            return True

    new_coord_generator = random_coordinates(dimensions)

    for old_coordinate in adj_coords:
        if old_coordinate in mice_set:
            # Remove the mouse
            set_value_on_board_nd(new_board, old_coordinate, 0)
            mice_set.remove(old_coordinate)

            # Find new location
            new_coordinate = next(new_coord_generator)
            # check until the new_coordinate is good
            while not good_new_coordinate(adj_coords, new_coordinate):
                new_coordinate = next(new_coord_generator)

            # Place mouse at new location
            set_value_on_board_nd(new_board, new_coordinate, "m")
            mice_set.add(new_coordinate)

    # now to add the numbers around the mice:
    for mice_coordinate in mice_set:
        neighbor_coordinates = get_adjacents_nd(dimensions, mice_coordinate)
        for neighbor_coordinate in neighbor_coordinates:
            if neighbor_coordinate in mice_set:
                continue
            else:
                set_value_on_board_nd(new_board, neighbor_coordinate, 1, add=True)

    # update the game board
    game["board"] = new_board


def reveal_nd(game, coordinates):
    """
    Recursively reveal square at coords and neighboring squares.

    Update the visible to reveal square at the given coordinates; then
    recursively reveal its neighbors, as long as coords does not contain and is
    not adjacent to a mouse.  Return a number indicating how many squares were
    revealed.  No action should be taken (and 0 should be returned) if the
    incoming state of the game is not 'ongoing', or if the given square has
    already been revealed.

    The updated state is 'lost' when at least one mouse is visible on the
    board, 'won' when all safe squares (squares that do not contain a mouse)
    and no mice are visible, and 'ongoing' otherwise.

    Parameters:
       coordinates (tuple): Where to start revealing squares

    Returns:
       int: number of squares revealed

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> reveal_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, 'm'], [3, 3], [1, 1], [0, 0]]
        [['m', 3], [3, 'm'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, False], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    >>> reveal_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, 'm'], [3, 3], [1, 1], [0, 0]]
        [['m', 3], [3, 'm'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: lost
    visible:
        [[False, True], [False, False], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    """
    has_bed = retrieve_val_nd(game["bed_board"], coordinates)
    # check if it's the first reveal
    if game["first_turn"]:
        # check if it's a bed
        if has_bed:
            return 0
        else:
            game["first_turn"] = False
            # move all these adj_coordinates
            move_(game, coordinates)
            # print('Move the mouse to new places')
            # dump(game)
            # print(game)

    def reveal_recurse(game, coordinates):

        # Check if the game is ongoing
        if game["state"] != "ongoing":
            return 0

        is_visible = retrieve_val_nd(game["visible"], coordinates)
        board_val = retrieve_val_nd(game["board"], coordinates)
        # Base case 1: Check if the cell is already revealed
        if is_visible:
            return 0

        # Base case 2: if the cell has a bed:
        has_bed = retrieve_val_nd(game["bed_board"], coordinates)
        if has_bed:
            # i.e the cell has a bed and shouldn't be revealed
            return 0

        # Reveal the current cell
        set_value_on_board_nd(game["visible"], coordinates, True)
        revealed = 1

        # Base case 3: if the clicked cell is a mouse and doesn't have a bed
        if board_val == "m":
            game["state"] = "lost"
            # print("You have lost the game!")
            return revealed

        # If current cell has no adjacent mines, recursively reveal neighbors
        if board_val == 0:
            dimensions = game["dimensions"]
            # Get all adjacent coordinates
            adj_coords = get_adjacents_nd(dimensions, coordinates)
            for adj_coord in adj_coords:
                # Skip the original coordinate if it's in the adjacents list
                if adj_coord == coordinates:
                    continue
                # Recursively reveal adjacent cells
                revealed += reveal_recurse(game, adj_coord)

        return revealed

    revealed = reveal_recurse(game, coordinates)
    win_check_nd(game)
    return revealed


def render_val(board_val, visible_val, bed_val, all_visible=False):
    """helper function that takes in the board value
    and changes it the rendering based on the value of
    visible board and bed board and all_visible."""
    if bed_val:
        if all_visible:
            return str(board_val) if board_val != 0 else " "
        else:
            return "B"
    else:
        if all_visible:
            return str(board_val) if board_val != 0 else " "
        else:
            if visible_val:
                return str(board_val) if board_val != 0 else " "
            else:
                return "_"


def render_nd(game, all_visible=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), 'm'
    (mice), ' ' (empty squares), or '1', '2', etc. (squares neighboring mice).
    The game['visible'] array indicates which squares should be visible.  If
    all_visible is True (the default is False), the game['visible'] array is
    ignored and all cells are shown.

    Parameters:
    all_visible (bool): Whether to reveal all tiles or just the ones allowed
                           by game['visible']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> reveal_nd(g, (0, 3, 0))
    8
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', 'm'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['m', '3'], ['3', 'm'], ['1', '1'], [' ', ' ']]]
    """

    def render_recurse(board, visi_board, bed_board, dims, all_visible=False):
        # base case:
        if len(dims) == 0:
            return render_val(board, visi_board, bed_board, all_visible)

        # recursive case:
        return [
            render_recurse(board[i], visi_board[i], bed_board[i], dims[1:], all_visible)
            for i in range(dims[0])
        ]

    board = game["board"]
    dimensions = game["dimensions"]
    visible_board = game["visible"]
    bed_board = game["bed_board"]

    return render_recurse(board, visible_board, bed_board, dimensions, all_visible)


def toggle_bed_2d(game, row, col):
    """function to add beds into the 2d game"""
    return toggle_bed_nd(game, (row, col))


def toggle_bed_nd(game, coordinates):
    """Function to add beds into the n-d game"""
    if game["state"] != "ongoing":
        return None

    is_visible = retrieve_val_nd(game["visible"], coordinates)
    # if it's already revealed
    if is_visible:
        return None

    else:  # that it is not visible
        has_bed = retrieve_val_nd(game["bed_board"], coordinates)
        set_value_on_board_nd(game["bed_board"], coordinates, not has_bed)
        return not has_bed


def random_coordinates(dimensions):
    """
    Given a tuple representing the dimensions of a game board, return an
    infinite generator that yields pseudo-random coordinates within the board.
    For a given tuple of dimensions, the output sequence will always be the
    same.
    """

    def prng(state):
        # see https://en.wikipedia.org/wiki/Lehmer_random_number_generator
        while True:
            yield (state := state * 48271 % 0x7FFFFFFF) / 0x7FFFFFFF

    prng_gen = prng(sum(dimensions) + 61016101)
    for _ in zip(range(1), prng_gen):
        pass
    while True:
        yield tuple(int(dim * val) for val, dim in zip(prng_gen, dimensions))


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d or any other function you might want.  To do so,
    # comment out the above line, and uncomment the below line of code.  This
    # may be useful as you write/debug individual doctests or functions.  Also,
    # the verbose flag can be set to True to see all test results, including
    # those that pass.
    #
    # doctest.run_docstring_examples(
    #    render_2d,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # )
    # game = new_game_2d(8, 8, [(6, 7), (2, 2), (4, 4), (4, 5), (6, 1)])
    # dump(game)
    # revealed = reveal_2d(game, 4, 4)
    # print(revealed)
    # dump(game)
