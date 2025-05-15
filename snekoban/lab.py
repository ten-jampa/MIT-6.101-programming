"""
6.1010 Lab:
Snekoban Game
"""

# import json # optional import for loading test_levels
# import typing # optional import
# import pprint # optional import

# NO ADDITIONAL IMPORTS!

DIRECTION_VECTOR = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}
##LOCATIONS IN THE TUPLE REPRESENTATION
PLAYER = 0
COMPUTERS = 1
FLAGS = 2
WALLS = 3
DIMENSIONS = 4


def make_new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    This function creates a tuple of the player position, the frozen set of positions
    of the computers, the frozen set of positions of the walls, and the frozen
    set of positions of the walls, and the dimensions of the level description.

    """
    player = None
    computers = set()
    targets = set()
    walls = set()
    # let's recover the dimensions to retrieve the level_description
    dim = (len(level_description), len(level_description[0]))
    for r, row in enumerate(level_description):
        for c, states in enumerate(row):
            if not states:  # i.e it's empty space
                continue
            for state in states:
                if state == "player":
                    player = (r, c)
                elif state == "computer":
                    computers.add((r, c))
                elif state == "target":
                    targets.add((r, c))
                elif state == "wall":
                    walls.add((r, c))
    return (player, frozenset(computers), frozenset(targets), frozenset(walls), dim)


def victory_check(game):
    """
    Given a game representation (of the form returned from make_new_game),
    return a Boolean: True if the given game satisfies the victory condition,
    and False otherwise.
    """
    computers_locs = game[COMPUTERS]
    flag_locs = game[FLAGS]
    if len(flag_locs) == 0:  # incase no targets avalailble
        return False
    return flag_locs == computers_locs


def get_next_gamestates(game):
    """Given the game representation, the function returns a dictionary
    with all the possible different gamestates from the four directions
    available.
    """
    next_gamestates = {}
    for direction in DIRECTION_VECTOR:
        if can_move(game, direction):
            new_game = step_game(game, direction)
            next_gamestates[direction] = new_game
    return next_gamestates


def copy_game(game):
    """A helper function to copy the gamestate"""
    return tuple(row for row in game)


def get_next_position(current, direction):
    """The function takes in a current position
    vector and returns the new position vector
    given the specified direction of travel"""
    return (
        current[0] + DIRECTION_VECTOR[direction][0],
        current[1] + DIRECTION_VECTOR[direction][1],
    )


def can_move(game, direction):
    """The function evaluates whether a move of the specified
    direction can be performed given the gamestate."""
    curr_position = game[PLAYER]
    next_position = get_next_position(curr_position, direction)
    if next_position in game[WALLS]:
        return False
    elif next_position in game[COMPUTERS]:
        next_next_position = get_next_position(next_position, direction)
        if next_next_position in game[COMPUTERS]:
            return False
        elif next_next_position in game[WALLS]:
            return False
    return True


def step_game(game, direction):
    """
    Given a game representation (of the form returned from make_new_game),
    return a game representation (of that same form), representing the
    updated game after running one step of the game.  The user's input is given
    by direction, which is one of the following:
        {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """

    new_game = copy_game(game)
    curr_position = game[PLAYER]
    next_position = get_next_position(curr_position, direction)
    if next_position in game[WALLS]:
        return new_game
    elif next_position in game[COMPUTERS]:
        next_next_position = get_next_position(next_position, direction)
        if next_next_position in game[COMPUTERS]:
            return new_game
        elif next_next_position in game[WALLS]:
            return new_game
        else:  # the computer moves
            altered_comp_locs = set(new_game[COMPUTERS] - {next_position})
            altered_comp_locs.add(next_next_position)
            return (
                next_position,
                frozenset(altered_comp_locs),
                new_game[FLAGS],
                new_game[WALLS],
                new_game[DIMENSIONS],
            )
    else:  # the player moves into space
        return (
            next_position,
            new_game[COMPUTERS],
            new_game[FLAGS],
            new_game[WALLS],
            new_game[DIMENSIONS],
        )


def dump_game(game):
    """
    Given a game representation (of the form returned from make_new_game),
    convert it back into a level description that would be a suitable input to
    make_new_game (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out
    the current state of your game for testing and debugging on your
    own.
    How efficient is this function right now? Can I do better?
    """
    row_dimension, col_dimensions = game[DIMENSIONS]
    canon_repr = [[[] for _ in range(col_dimensions)] for _ in range(row_dimension)]
    # insert player
    player_loc = game[PLAYER]
    canon_repr[player_loc[0]][player_loc[1]] += ["player"]
    # insert the computers
    computer_locs = game[COMPUTERS]
    for comp_loc in computer_locs:
        canon_repr[comp_loc[0]][comp_loc[1]] += ["computer"]
    # insert the flags
    target_locs = game[FLAGS]
    for target_loc in target_locs:
        canon_repr[target_loc[0]][target_loc[1]] += ["target"]
    # insert the walls
    wall_locs = game[WALLS]
    for wall_loc in wall_locs:
        canon_repr[wall_loc[0]][wall_loc[1]] += ["wall"]
    return canon_repr


def solve_puzzle(game, search="BFS", verbose=False):
    """
    Given a game representation (of the form returned from make_new_game), the function
    finds a solution or returns None if no solutions are found.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """
    if victory_check(game):  # see if the game has already been solved
        return []
    ini_gamestate = game
    agenda = [(ini_gamestate, [])]  # agenda: gamestate, and [direction]
    visited_game_states = {ini_gamestate}
    while agenda:
        if verbose:  # incase I want to know how whether a search is narrowing down
            print(f"items left on agenda: {len(agenda)}")
        curr_gamestate, curr_path = agenda.pop(0)
        next_gamestates = get_next_gamestates(curr_gamestate)
        for direc, next_gamestate in next_gamestates.items():
            new_path = curr_path + [direc]
            if victory_check(next_gamestate):
                return new_path
            if next_gamestate in visited_game_states:
                continue
            visited_game_states.add(next_gamestate)
            if search == "BFS":
                agenda.append((next_gamestate, new_path))
            elif search == "DFS":
                agenda.insert(0, (next_gamestate, new_path))
    return None


if __name__ == "__main__":
    #     amp = [
    #   [["wall"], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"]],
    #   [["wall"], [], ["player"], ["computer"], ["target"], ["wall"]],
    #   [["wall"], [], ["wall"], [], [], ["wall"]],
    #   [["wall"], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"]]
    # ]
    #     amp_game = make_new_game(amp)
    #     print(amp_game)
    #     reamp = dump_game(amp_game)
    #     end = solve_puzzle(amp_game, "BFS")
    pass
