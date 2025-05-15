"""
6.101 Lab:
LISP Interpreter Part 2
"""

#!/usr/bin/env python3
import sys

sys.setrecursionlimit(20_000)


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


class SchemeSyntaxError(SchemeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
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
    tokens = []
    current_token = ""
    i = 0
    n = len(source)

    while i < n:
        char = source[i]

        # Handle comments
        if char == ";":
            # Skip everything until a newline
            while i < n and source[i] != "\n":
                i += 1

        # Handle parentheses
        elif char == "(" or char == ")":
            if current_token:
                tokens.append(current_token)
                current_token = ""
            tokens.append(char)

        # Handle whitespace
        elif char.isspace():
            if current_token:
                tokens.append(current_token)
                current_token = ""

        else:
            current_token += char
        i += 1

    # Add the last token if there is one
    if current_token:
        tokens.append(current_token)

    return tokens


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

            if index >= len(tokens):
                raise SchemeSyntaxError

            while tokens[index] != stop:
                sub_expression, index = recursive_parse(index)
                out.append(sub_expression)
                if index >= len(tokens):
                    raise SchemeSyntaxError

            return (
                out,
                index + 1,
            )  # Move past the ')' # we have no error here because we have started a paranthesis

        elif token == stop:
            # we have a rogue end bracket
            raise SchemeSyntaxError("T")

        else:
            # Base Case
            return number_or_symbol(token), index + 1

    # Parse the tokens starting at index 0
    parsed_expression, end_index = recursive_parse(0)
    if end_index < len(tokens):
        raise SchemeSyntaxError(
            f"Parsed Expression is { parsed_expression} and end_index is {end_index}"
        )
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


### Boolean Builtin Function ###


def is_equal(*args):
    """Function to check the equality of
    arbitrary many values"""

    if len(args) < 2:
        raise SchemeError("equal? requires at least two arguments")
    return all(x == args[0] for x in args[1:])


def is_greater(*args):
    """Function to check the Greater than relation
    of arbitrary many values"""

    if len(args) < 2:
        raise SchemeError("Greater than evaluation requires at least two arguments")
    return all(x > y for x, y in zip(args, args[1:]))


def is_geq(*args):
    if len(args) < 2:
        raise SchemeError("GEQ evaluation requires at least two arguments")
    return all(x >= y for x, y in zip(args, args[1:]))


def is_less(*args):

    if len(args) < 2:
        raise SchemeError("Less than evaluation requires at least two arguments")
    return all(x < y for x, y in zip(args, args[1:]))


def is_leq(*args):

    if len(args) < 2:
        raise SchemeError("Less than evaluation requires at least two arguments")
    return all(x <= y for x, y in zip(args, args[1:]))


def negate(*truth_value):
    if len(truth_value) != 1:
        raise SchemeEvaluationError
    return not truth_value[0]


def begin(code, initial_frame):
    if len(code) == 1:
        return evaluate(code[0], initial_frame)
    # more than one expression
    out_val = None
    for expr in code:
        out_val = evaluate(expr, initial_frame)
    return out_val


###### Cons and LList  ####


class Pair:
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr

    def __repr__(self, first=True):
        car = self.car
        cdr = self.cdr

        # Base case: End of the list
        if not isinstance(cdr, Pair):
            if cdr is None:
                if first:
                    return f"List: [{car}]"
                return f"{car}]"
            else:
                return f"Cons: {car, cdr}"

        # Recursive case: Add current element and continue
        if first:
            return f" List: [{car}, {cdr.__repr__(first=False)}"
        else:
            return f"{car}, {cdr.__repr__(first=False)}"

    def is_just_cons(self):
        if self.cdr is None:
            return False  # Proper list (linked list)
        if isinstance(self.cdr, Pair):
            return self.cdr.is_just_cons()
        return True  # Dotted pair

    def is_ll(self):
        return not self.is_just_cons()

    def __len__(self):
        if self.is_just_cons():
            raise SchemeEvaluationError("Cannot calculate length of an improper list.")
        if self.cdr is None:
            return 1
        return 1 + len(self.cdr)

    def __getitem__(self, index):
        car = self.car
        cdr = self.cdr
        if index == 0:
            return car
        else:
            if isinstance(cdr, Pair):
                index -= 1
                return cdr.__getitem__(index)
            else:
                raise SchemeEvaluationError(f"Index {index} is out of bounds")

    def __iter__(self):
        """Generator of (cars) in the self"""
        car = self.car
        cdr = self.cdr
        curr_cdr = cdr
        yield car
        while isinstance(curr_cdr, Pair):
            yield curr_cdr.car
            curr_cdr = curr_cdr.cdr

        if curr_cdr is not None:
            yield curr_cdr


###################################
# Functions for Cons and LL #######
#################################


def get_car(*pair_obj):
    if len(pair_obj) != 1:
        raise SchemeEvaluationError
    pair_obj = pair_obj[0]
    if not isinstance(pair_obj, Pair):
        raise SchemeEvaluationError
    return pair_obj.car


def get_cdr(*pair_obj):
    if len(pair_obj) != 1:
        raise SchemeEvaluationError
    pair_obj = pair_obj[0]
    if not isinstance(pair_obj, Pair):
        raise SchemeEvaluationError
    return pair_obj.cdr


def con(*args):
    if len(args) != 2:
        raise SchemeEvaluationError

    car = args[0]
    cdr = args[1]
    pair_con = Pair(car, cdr)
    return pair_con


def make_list(*args):
    if not args:
        return None

    if len(args) == 1:
        return con(args[0], None)

    first, *rest = args
    return con(first, make_list(*rest))


def is_llist(*object):
    ## either no objects were given
    ## or more than one object
    if len(object) != 1:
        raise SchemeEvaluationError

    ## Empty List
    if object[0] is None:
        return True

    ## It's not a Pair object
    if not isinstance(object[0], Pair):  # it's not a pair
        return False
    return object[0].is_ll()


def get_length(*object):
    if not is_llist(*object):
        raise SchemeEvaluationError

    object = object[0]
    if not is_llist(object):
        raise SchemeEvaluationError
    if object is None:
        return 0
    else:
        return len(object)


def ll_get(*args):
    if len(args) != 2:
        raise SchemeEvaluationError
    cons, index = args[0], args[1]
    if not isinstance(cons, Pair):
        raise SchemeEvaluationError
    return cons[index]


def append(*lists):
    if not lists:
        return None  # No lists to append

    # Base case: Single list
    if len(lists) == 1:
        if is_llist(*lists):
            return lists[0]
        else:
            raise SchemeEvaluationError

    first, *rest = lists
    if first is None:  # Skip empty list
        return append(*rest)

    if not isinstance(first, Pair):
        raise SchemeEvaluationError("First argument is not a proper list.")

    if not is_llist(first):
        raise SchemeEvaluationError

    # Recursively append the rest of the lists
    return Pair(first.car, append(first.cdr, *rest))


#######

scheme_builtins = {
    "+": lambda *args: sum(args),
    "-": calc_sub,
    "*": calc_product,
    "/": calc_division,
    ### boolean Evaluations
    "equal?": is_equal,
    ">": is_greater,
    ">=": is_geq,
    "<": is_less,
    "<=": is_leq,
    "not": negate,
    ##Boolean Values
    "#t": True,
    "#f": False,
    ## Con/List
    "cons": con,
    "car": get_car,
    "cdr": get_cdr,
    "list": make_list,
    "list?": is_llist,
    "length": get_length,
    "list-ref": ll_get,
    "append": append,
    ### Flow
    "begin": begin,
}


######################
# Frame Objects and Functions #
######################


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

    def __init__(self, bindings=None, parent=None):
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
        bindings = self.bindings
        parent_frame = self.parent
        return Frame(bindings, parent_frame)

    def generate_child(self):
        return Frame(bindings=None, parent=self)

    def set_bang(self, var, value):
        if var in self.bindings:
            self[var] = value
        else:
            # Recursively look to my parents
            self.parent.set_bang(var, value)

    def __contains__(self, name):
        """
        Check if a variable is in the current frame or parent frames.
        """
        if name in self.bindings:
            return True
        elif self.parent:  #
            # Ask the Parent frame
            return name in self.parent
        else:
            return False


class SchemaFunctions:
    """Function object to represent the functions
    being defined or evaluated."""

    def __init__(self, enclosing_frame, params, expr):
        self.params = params
        self.enclosing_frame = enclosing_frame  # we get a new frame
        self.body = expr

    def __call__(self, *param_values):
        # New Frame with parent pointer
        func_frame = self.enclosing_frame.generate_child()

        # Bind parameter values in the new frame
        if len(self.params) != len(param_values):
            raise SchemeEvaluationError("Function expects a different number of inputs")

        for variable, value in zip(self.params, param_values):
            func_frame[variable] = value

        # Evaluate the function body in the new frame
        return evaluate(self.body, func_frame)


def make_initial_frame():
    """To make a function frame inheriting the built-ins
    from the Global Fram"""
    return Frame(parent=GlobalFrame())


##############
# Evaluation #
##############

### Eval Helper Functions for Special Forms ###


def evaluate_lambda(tree, initial_frame):
    parameters, expr = tree[0], tree[1]
    schema_func = SchemaFunctions(initial_frame, parameters, expr)
    return schema_func


def evaluate_define(tree, initial_frame):
    Name, Expr = tree[0], tree[1]
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


def evaluate_and(tree, initial_frame):
    # quick_check
    if "#f" in tree:
        return False

    bool_val = None
    for expr in tree:
        if bool_val is None:
            bool_val = evaluate(expr, initial_frame)
        else:
            bool_val = bool_val and evaluate(expr, initial_frame)
        if bool_val == False:
            return False
    return True


def evaluate_or(tree, initial_frame):
    # quick check
    if "#t" in tree:
        return True

    bool_val = None
    index = 0
    for expr in tree:
        if bool_val is None:
            bool_val = evaluate(expr, initial_frame)
        else:
            bool_val = evaluate(expr, initial_frame)
        if bool_val:
            return True
    return False


def evaluate_if(tree, initial_frame):
    # generic structure of IF
    # (IF Predicate True_Exp False_exp)
    if len(tree) != 3:
        raise SchemeEvaluationError(f"Conditional not properly given")
    Pred, TE, FE = tree[0], tree[1], tree[2]
    eval_pred = evaluate(Pred, initial_frame)
    if eval_pred == True:
        return evaluate(TE, initial_frame)
    elif eval_pred == False:
        return evaluate(FE, initial_frame)
    else:
        raise SchemeEvaluationError(f"Predicate does not give a boolean value")


def evaluate_let(tree, initial_frame):
    if len(tree) != 2:
        raise SchemeEvaluationError

    var_val_bindings, body = tree[0], tree[1]
    ## Build the temporary local frame
    local_frame = initial_frame.generate_child()
    for expr in var_val_bindings:
        evaluate_define(expr, local_frame)
    ## having updated the local frame
    return evaluate(body, local_frame)


def evaluate_set(tree, initial_frame):
    var, expr = tree[0], tree[1]
    if var not in initial_frame:
        raise SchemeNameError
    eval_expr = evaluate(expr, initial_frame)
    initial_frame.set_bang(var, eval_expr)
    return evaluate(var, initial_frame)


def evaluate_del(tree, initial_frame):
    var = tree[0]
    if var in initial_frame.bindings:
        return initial_frame.bindings.pop(var)
    else:
        raise SchemeNameError


special_forms = {
    "define": evaluate_define,
    "lambda": evaluate_lambda,
    "if": evaluate_if,
    "and": evaluate_and,
    "or": evaluate_or,
    "begin": begin,
    "del": evaluate_del,
    "let": evaluate_let,
    "set!": evaluate_set,
}

#### Main Evaluate function ####


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
        # print(f'Tree: {tree}', flush=True)

    # number
    if isinstance(tree, (int, float)):
        return tree

    # string
    elif isinstance(tree, str):
        if tree in initial_frame:
            return initial_frame[tree]
        else:
            raise SchemeNameError(
                f"Error with value {tree}, could not find in current Frame"
            )

    # S_expression (with special forms)
    elif isinstance(tree, list):
        # empty list ()
        if len(tree) == 0:
            return None

        first, rest = tree[0], tree[1:]
        if isinstance(first, str) and first in special_forms:
            return special_forms[first](rest, initial_frame)

        ##Callable Function
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


######## Reading from Files


def evaluate_file(filename, initial_frame=None):
    with open(filename, mode="r") as f:
        scheme_code = f.read()
        expression = make_expression(scheme_code)
        return evaluate(expression, initial_frame)


#####################

if __name__ == "__main__":
    import os

    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    import schemerepl

    print(sys.argv)
    my_env = make_initial_frame()
    for file in sys.argv[1:]:
        evaluate_file(file, my_env)
    schemerepl.SchemeREPL(
        sys.modules[__name__], use_frames=True, verbose=False, repl_frame=my_env
    ).cmdloop()
