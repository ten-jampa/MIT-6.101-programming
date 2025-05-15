"""
6.101 Lab:
LISP Interpreter Part 1
"""

#!/usr/bin/env python3

# import doctest # optional import
# import typing  # optional import
# import pprint  # optional import

import sys

sys.setrecursionlimit(20_000)

# NO ADDITIONAL IMPORTS!

#############################
# Scheme-related Exceptions #
#############################


class SchemeError(Exception):
    """
    A type of exception to be raised if there is an error with a Scheme
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class SchemeNameError(SchemeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class SchemeEvaluationError(SchemeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SchemeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(value):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value

def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens,
    right parens,
    other whitespace-separated values).  Returns a list of strings.
    Arguments:
        source (str): a string containing the source code of a Scheme
                    expression
    """
    start_stop = {"(", ")"}
    space = " "
    comment = ";"
    next_line = "\n"
    out_tokens = []
    prev_token = None
    comment_mode = False

    for char in source:

        if comment_mode:
            if char is next_line:
                comment_mode = False
            continue

        if char is space:
            if prev_token:
                out_tokens.append(prev_token)
                prev_token = None
                continue
            else:
                continue
        if char is comment:
            comment_mode = True
            continue

        if char is next_line:
            if comment_mode:
                comment_mode = False
                continue
            else:
                if prev_token:
                    out_tokens.append(prev_token)
                    prev_token = None
                    continue
        if char in start_stop:
            if prev_token:
                out_tokens.append(prev_token)
                out_tokens.append(char)
                prev_token = None
            else:
                out_tokens.append(char)
        else:
            if prev_token:
                prev_token += char
            else:
                prev_token = char

    if prev_token:
        out_tokens.append(prev_token)
    return out_tokens


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    # tokens will be a list
    start = "("
    stop = ")"

    def recursive_parse(index):
        """Recursively parses the tokens to build the expression."""
        token = tokens[index]

        if token == start:
            # we have an expression
            out = []
            index += 1  # Move past the '('
            while tokens[index] != stop:
                sub_expression, index = recursive_parse(index)
                out.append(sub_expression)
            return out, index + 1  # Move past the ')'
        else:
            # Base Case
            return number_or_symbol(token), index + 1

    # Parse the tokens starting at index 0
    parsed_expression, _ = recursive_parse(0)
    return parsed_expression


def make_expression(source):
    """To go from scheme source code to the parsed tree"""
    tokens = tokenize(source)
    parsed = parse(tokens)
    return parsed


######################
# Built-in Functions #
######################


def calc_sub(*args):
    """Subtraction function of arbitrary arguments"""
    if len(args) == 1:
        return -args[0]

    first_num, *rest_nums = args
    return first_num - scheme_builtins["+"](*rest_nums)


def calc_product(*args):
    """Production function of arbitrary arguments"""
    if len(args) == 1:
        return args[0]
    out_product = 1
    for num in args:
        out_product *= num
    return out_product


def calc_division(*args):
    """Division function of arbitrary arguments"""
    if not args:
        raise ValueError("No numbers to divide")
    if len(args) == 1:
        return 1 / args[0]
    first_num, *rest_nums = args
    return first_num / scheme_builtins["*"](*rest_nums)


scheme_builtins = {
    "+": lambda *args: sum(args),
    "-": calc_sub,
    "*": calc_product,
    "/": calc_division,
}


def make_initial_frame():
    """To make a function frame inheriting the built-ins
    from the Global Fram"""
    return Frame(parent=GlobalFrame())


class GlobalFrame:
    """Global Frame where the built-ins of the language
    are stored"""

    bindings = scheme_builtins

    def __init__(self):
        """
        The global frame.
        """
        pass

    def __setitem__(self, name, value):
        """
        Set a variable in the current frame.
        """
        self.bindings[name] = value

    def __str__(self):
        out_str = "--------------------- \n"
        for key, val in self.bindings.items():
            line_string = " Variable: " + str(key) + ", Value: " + str(val) + " \n "
            out_str += line_string
        return out_str + "\n"

    def __getitem__(self, name):
        """
        Get a variable from the current frame.
        """
        if name in self.bindings:
            return self.bindings[name]
        else:
            raise SchemeNameError(f"Variable '{name}' not found")

    def __contains__(self, name):
        """
        Check if a variable is in the current frame.
        """
        return name in self.bindings


class Frame(GlobalFrame):
    """Frame Object to store local variables
    and point to its parent frame"""

    def __init__(self, bindings = None, parent=None):
        """
        Initialize a frame with an optional parent frame.
        """
        if bindings is None:
            self.bindings = {}
        else:
            self.bindings = bindings
        self.parent = parent  # Reference to the parent frame

    def __setitem__(self, name, value):
        """
        Set a variable in the current frame.
        """
        self.bindings[name] = value

    def __str__(self):
        # current_frame_bindings

        this_frame_str = GlobalFrame.__str__(self)

        # recursively form the string representation of the parent frames
        parent_frame = self.parent
        out_str1 = "Current Frame \n"
        out_str2 = "Parent \n"
        return out_str1 + this_frame_str + out_str2 + parent_frame.__str__()

    def __getitem__(self, name):
        """
        Get a variable from the current frame or parent frames.
        """
        if name in self.bindings:
            return self.bindings[name]
        elif self.parent:
            # Recursively look backwards
            return self.parent[name]
        else:
            raise SchemeNameError(f"Variable '{name}' not found")

    def copy(self):
        bindings = self.bindings.copy()
        parent = self.parent
        return Frame(bindings, parent)

    def __contains__(self, name):
        """
        Check if a variable is in the current frame or parent frames.
        """
        if name in self.bindings:
            return True
        elif self.parent:
            # Ask the Parent frame
            return name in self.parent
        else:
            return False


class SchemaFunctions:
    """Function object to represent the functions
    being defined or evaluated."""

    def __init__(self, enclosing_frame, params, expr):
        self.params = params
        self.enclosing_frame = enclosing_frame
        self.body = expr

    def __call__(self, *param_values):
        # New Frame with parent pointer
        func_frame = self.enclosing_frame.copy()

        # Bind parameter values in the new frame
        if len(self.params) != len(param_values):
            raise SchemeEvaluationError("Function expects a different number of inputs")

        for variable, value in zip(self.params, param_values):
            func_frame[variable] = value

        # Evaluate the function body in the new frame
        return evaluate(self.body, func_frame)


##############
# Evaluation #
##############


def evaluate(tree, initial_frame=None):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    if initial_frame is None:
        initial_frame = make_initial_frame()

    # number
    if isinstance(tree, (int, float)):
        return tree

    # string
    elif isinstance(tree, str):
        if tree in initial_frame:
            return initial_frame[tree]
        else:
            raise SchemeNameError(
                f"Error with value {tree}, could not find in {initial_frame}"
            )

    # S_expression
    elif tree[0] == "lambda":
        parameters, expr = tree[1], tree[2]
        schema_func = SchemaFunctions(initial_frame, parameters, expr)
        return schema_func

    elif tree[0] == "define":
        Name, Expr = tree[1], tree[2]
        # am I shorthandedly defining a function?
        # if so, then the Name is a list with arguments
        if isinstance(Name, list):
            name, *args = Name
            schema_func = SchemaFunctions(initial_frame, args, Expr)
            initial_frame[name] = schema_func
            return schema_func
        else:
            evaluated_val = evaluate(Expr, initial_frame)
            initial_frame[Name] = evaluated_val
            # print(initial_frame)
            return evaluated_val

    elif isinstance(tree, list):
        first, rest = tree[0], tree[1:]
        first_func = evaluate(first, initial_frame)
        if not callable(first_func):
            raise SchemeEvaluationError(
                f"First term in the expression {tree} is not a callable function"
            )
        # print(initial_frame, flush=True)
        return first_func(*[evaluate(ir, initial_frame) for ir in rest])

    # otherwise
    else:
        raise SchemeEvaluationError("Improper parsed input")


if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)
    import os

    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    import schemerepl

    schemerepl.SchemeREPL(
        sys.modules[__name__], use_frames=True, verbose=True
    ).cmdloop()
    # circle_tokens = tokenize('(define circle-area (lambda (r) (* 3.14 (* r r))))')
    # print(circle_tokens)
    # print(parse(circle_tokens))
    pass
