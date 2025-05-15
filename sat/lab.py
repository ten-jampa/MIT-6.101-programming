"""
6.101 Lab:
SAT Solver
"""

#!/usr/bin/env python3

# import typing  # optional import
# import pprint  # optional import
import doctest
import sys

sys.setrecursionlimit(10_000)
# NO ADDITIONAL IMPORTS


def contradiction_check(formula):
    """Contradiction check"""
    if [] in formula:
        return True
    else:
        return False


def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> T, F = True, False
    >>> x = satisfying_assignment([[('a', T), ('b', F), ('c', T)]])
    >>> x.get('a', None) is T or x.get('b', None) is F or x.get('c', None) is T
    True
    >>> satisfying_assignment([[('a', T)], [('a', F)]])
    """

    def recurse_satisfying_assignment(formula, curr_solutions={}, all_variables=set()):
        if not all_variables:
            all_variables = get_all_variables(formula)

        ## Base cases:
        # 1: if the formula is empty []:
        if not formula:
            return curr_solutions

        # 2. if the formula contains unresovable clauses like [[], [('a', True)]]:
        if [] in formula:
            return None

        new_variable = all_variables.pop()

        # two options similarly

        for bool in [True, False]:
            set_literal = (new_variable, bool)
            curr_solutions[new_variable] = bool
            new_formula = update_formula(formula, set_literal)
            if new_formula is not None:
                new_formula, curr_solutions = simplify_CNF(new_formula, curr_solutions)
                if new_formula is None:
                    continue
                new_all_variables = all_variables - set(curr_solutions.keys())
                attempt = recurse_satisfying_assignment(
                    new_formula, curr_solutions, new_all_variables
                )
                if attempt is not None:
                    return attempt
        # NO SOLUTIONS
        return None

    simplified_formula, initial_solutions = simplify_CNF(formula)
    if simplified_formula is None:
        return None
    all_variables = get_all_variables(formula)
    new_all_variables = all_variables - set(initial_solutions.keys())
    return recurse_satisfying_assignment(
        simplified_formula, initial_solutions, new_all_variables
    )


def has_unit_clause(formula):
    """Checks if a given CNF formula
    has unit clauses, exits straightaway"""
    for clause in formula:
        if len(clause) == 1:
            return True
    return False


def simplify_CNF(formula, out=None):
    """Given a CNF formula, this function simplies
    the formula by removing unit clauses and
    returns the modified formula with the variable assignements"""
    if out is None:
        out = {}

    new_formula = formula

    if not has_unit_clause(new_formula):
        return new_formula, out

    for clause in new_formula:
        if len(clause) == 1:
            literal = clause[0]
            var, val = literal
            out[var] = val
            new_formula = update_formula(new_formula, literal)
            if new_formula is None:
                return None, out
            return simplify_CNF(new_formula, out)
    return new_formula, out


def get_all_variables(formula):
    """Given a CNF formula, this function retrieves
    all the string variables and returns it."""
    var_set = set()
    for clause in formula:
        for var, _ in clause:
            if var not in var_set:
                var_set.add(var)
    return var_set


def update_formula(formula, set_literal):
    """With the Literal form of ('a', True/False),
    given the literal, we move through each clauses in the formula and
    update to a new formula."""

    ###New
    new_formula = []
    set_var, set_val = set_literal
    for clause in formula:
        skip_flag = False
        # Check if the clause is satisfied by the set_literal
        for var, val in clause:
            if (var == set_var) and (val == set_val):
                skip_flag = True
                break  # clause is satisfied, skip it

        # Otherwise, remove the negated literal from the clause
        if skip_flag:
            continue
        else:
            new_clause = [(var, val) for (var, val) in clause if var != set_var]
            if not new_clause:
                return None
            # print(new_clause)
            new_formula.append(new_clause)

    return new_formula


##### PART 2: ########
def get_rooms(student_preferences):
    """Given the students preferences dictionary,
    this function retrieves the rooms as a set."""
    out = set()
    for values in student_preferences.values():
        out |= values
    return out


def create_literals_for_student(student, students_preferences, bool=False):
    """Given a student and the preferences dictionary,
    the function returns the set of literals that can be created
    with a specified boolean value, which defaults to False"""
    out = set()
    preferences = get_rooms(students_preferences)
    for preference in preferences:
        variable = student + "_" + preference
        literal = (variable, bool)
        out.add(literal)
    return out


def create_all_clauses_student(student, students_preferences):
    """Given a student and the student preferences,
    the function returns a list of all the all_clauses
    that can be made to check for rule 2."""
    all_student_literals = create_literals_for_student(student, students_preferences)
    all_clause = []
    seen = set()
    for literal1 in all_student_literals:
        for literal2 in all_student_literals:
            joint = (literal1, literal2)
            reverse = (literal2, literal1)
            if literal2 == literal1:
                continue
            elif (reverse in seen) or (joint in seen):
                continue
            else:
                seen.add(joint)
                seen.add(reverse)
                clause = [(literal1), (literal2)]
                all_clause.append(clause)
    return all_clause


def get_all_group(room, capacity, students):
    """Given a room, its capacity, and the list of
    students, the function returns a set of all (capacity+1) length
    tuples possibles with the given list of students."""
    out = set()

    # Base case
    if capacity == 0:
        return [(student + "_" + room,) for student in students]

    # Recursive case
    else:
        capacity -= 1
        for i, student1 in enumerate(students):
            copied_students = students[i + 1 :]
            for rest_students in get_all_group(room, capacity, copied_students):
                combo = tuple(sorted((student1 + "_" + room,) + rest_students))
                out.add(combo)
    return list(out)


def make_clauses_from_group(room, capacity, students):
    """Given a room, its capacity, and the list of students,
    returns the clause that is made to be fed into making rule 3."""
    all_groups = get_all_group(
        room, capacity, students
    )  # a list of tuples where each tuple is length (capcity+1) possible with student and room name
    main_formula = []  # main formula will be a conjuction of AND of the sub clauses
    for group in all_groups:
        sub_formula = []
        for i, sub_group in enumerate(group):
            sub_formula.append((sub_group, False))
        main_formula.append(sub_formula)
    return main_formula


def rule1(students_preference):
    """Returns the CNF formula, given the students preferences,
    according to the first rule:
    That all of the student's preference are satisfied."""
    main_formula = []
    for student, preferences in students_preference.items():
        sub_formula = []
        for preference in preferences:
            variable = student + "_" + preference
            literal = (variable, True)
            sub_formula.append(literal)
        main_formula.append(sub_formula)
    return main_formula


def rule2(students_preference):
    """Returns the CNF formula, given the students preference,
    according to the second rule:
    That a student is not in more than one of their preferred rooms."""
    main_formula = []
    for student in students_preference.keys():
        student_clauses = create_all_clauses_student(student, students_preference)
        for not_clause in student_clauses:
            main_formula.append(not_clause)
    return main_formula


def rule3(students_preferences, room_capacities):
    """Given the dictionary of student preference,
    and room capcities, the function returns the CNF formula
    according to the third rule:
    That the room capacities are not exceeded."""
    students = list(students_preferences.keys())
    rooms = list(room_capacities.keys())
    out_formula = []
    for room in rooms:
        capacity = room_capacities[room]
        if capacity >= len(students):
            continue
        clause = make_clauses_from_group(room, room_capacities[room], students)
        # print(clause)
        out_formula += clause
    return out_formula


def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Convert a quiz-room-scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a set
                         of room names (strings) that work for that student

    room_capacities: a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up

    We assume no student or room names contain underscores.
    """
    rule1_formula = rule1(student_preferences)
    rule2_formula = rule2(student_preferences)
    rule3_forumla = rule3(student_preferences, room_capacities)
    return rule1_formula + rule2_formula + rule3_forumla


if __name__ == "__main__":
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
    base_formula = [
        [("a", False), ("b", False)],
        [("a", True), ("d", False)],
        [("a", True)],
        [("a", False), ("e", True), ("f", False), ("g", True)],
        [("b", True), ("c", True), ("f", True)],
        [("b", False), ("f", True), ("g", False)],
    ]
    print(update_formula(base_formula, ("a", True)))
    # print(simplify_CNF(base_formula))
    # print(satisfying_assignment(base_formula))
