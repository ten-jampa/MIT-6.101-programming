"""
6.1010 Spring 2023
Lab04 Optional Practice Exercises: Puzzle
"""

direction_offsets = {"up": (-1, 0), "down": (1, 0), "right": (0, 1), "left": (0, -1)}


def find_blank(board):
    """
    Given a board, find the location of the single blank space (None).

    Parameters:
        board: a list of row lists containing the board values.

    Returns:
        The (row, column) tuple of the blank space location.
    """
    for r, row in enumerate(board):
        for c, val in enumerate(row):
            if val == None:
                return r,c


def goal_test(state):
    '''
    Helper function for solve puzzle.
    Make a goal_test function that takes in a state from solve_puzzle and 
    returns True if the state represents a solved puzzle, False otherwise
    '''
    i = 1
    for _, val in state:
        if val != i:
            return False
        else:
            i += 1
    

def get_neighbors(state):
    """
    Helper function for solve_puzzle.
    Given a state from solve_puzzle, return a list of neighbor states.
    """
    copied_state = tuple(row for row in state)
    blank_loc = find_blank(state)
    return None

POSITIONS = 0
VALUE = 1
ROW = 0
COL = 1

def get_state(board):
    outlist = []
    for r, row in enumerate(board):
        for c, val in enumerate(row):
            outlist.append(((r,c),val))
    return outlist

def solve_puzzle(board):
    """
    Given a puzzle board, return the boards needed to solve the puzzle
    move by move.

    Parameters: 
        board: a list of row lists containing the board values.
    
    Returns:
        A list of board states (either in tuple or list form) representing each
        move needed to solve the puzzle. Returns None if there is no way to 
        solve the puzzle from given start board.
    """
    start = get_state(board)
    # how will you represent the state?

    if goal_test(start):
        return [] # what should we return?
    
    agenda = [(start,[])]  # what will the agenda store?
    visited = {start}

    while agenda:
        current = agenda.pop(0)
        # what is the current_state?
        last_state = current[0]
        cur_path = current[-1]
        for neighbor in get_neighbors(current):
            if neighbor not in visited:
                if goal_test(neighbor):
                    return True# return a list of board states
                new_path = cur_path + []
                # new_agenda = ?
                agenda.append(new_agenda)
                visited.add(neighbor)


### HELPER FUNCTIONS
def print_board(board):
    """
    Given a board, print it out in aligned rows.
    """
    for row in board:
        print(
            f"{'  '.join([' '+str(num) if num is not None and num < 10 else str(num) if num is not None else ' X' for num in row]):25}"
        )


def move_board(blank_loc, board, direction):
    """
    Given a blank_loc, a board, and a direction return the new blank loc and
    the new board that results from moving the blank in the given direction.

    Parameters:
        blank_loc: a (row, col) tuple of the None tile location.
        board: a list of row-lists containing board values.
        direction: string, one of "up", "down", "left", "right".

    Returns:
        A (new_blank_loc, new_board) without modfying the inputs.

    """
    new_loc = tuple(x + dx for x, dx in zip(blank_loc, direction_offsets[direction]))

    # can the blank move to the new location?
    if 0 <= new_loc[0] < len(board) and 0 <= new_loc[1] < len(board[0]):
        # make mutable copy of the board
        new_board = [list(row) for row in board]
        # swap tiles
        new_board[blank_loc[0]][blank_loc[1]] = new_board[new_loc[0]][new_loc[1]]
        new_board[new_loc[0]][new_loc[1]] = None
        return new_loc, new_board

    return blank_loc, board  # can't move out of bounds!


if __name__ == "__main__":
    # Feel free to test your code in the space below:
    puzzle = ((1, 2, 8, 3), (5, 6, 7, 4), (13, 9, 12, None), (14, 11, 10, 15))
    puzzle_blank = (2, 3)
    puzzle2 = ((1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), (None, 13, 14, 15))
    puzzle_blank2 = (3,0)
    initial_board = ((1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), (13, 14, 15, None))
    initial_blank = (3, 3)
    print_board(puzzle)
    print("solving puzzle...")
    path = []#solve_puzzle(puzzle)
    for i, pboard in enumerate(path):
        print(f"Move {i}")
        print_board(pboard)
        print()
