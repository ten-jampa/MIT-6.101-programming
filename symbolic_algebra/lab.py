"""
6.101 Lab:
Symbolic Algebra
"""

# import doctest # optional import
# import typing # optional import
# import pprint # optional import
# import string # optional import
# import abc # optional import

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Expr:
    """Most fundamental class that defines a symbolic
    expression"""

    def precedence(self):
        return 10  # a high number

    def __add__(self, other):
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __sub__(self, other):
        return Sub(self, other)

    def __rsub__(self, other):
        return Sub(other, self)

    def __mul__(self, other):
        return Mul(self, other)

    def __rmul__(self, other):
        return Mul(other, self)

    def __truediv__(self, other):
        return Div(self, other)

    def __rtruediv__(self, other):
        return Div(other, self)


class Var(Expr):
    """Class to define variables to be used in
    symbolic expression"""

    def __init__(self, name):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = name

    def evaluate(self, mapping):
        if self.name in mapping:
            return mapping[self.name]
        else:
            raise SymbolicEvaluationError("Value for one or more variables is missing")

    def deriv(self, variable):
        if variable == self.name:
            return Num(1)
        else:
            return Num(0)

    def __eq__(self, other):
        return self.name == other.name

    def simplify(self):
        return self

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Var('{self.name}')"


class Num(Expr):
    """Class to define number object to be used in
    symbolic algebra"""

    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n

    def deriv(self, variable):
        # constant differentiation
        return Num(0)

    def __eq__(self, other):
        return self.n == other.n

    def evaluate(self, mapping):
        return self.n

    def simplify(self):
        return self

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return f"Num({self.n})"


## Classes of Binary Operators
class BinOp(Expr):
    """Class that represents a Binary Operator of
    some operation between a left symbolic expression and
    a right symbolic expression."""

    def __init__(self, left, right, Op):
        # check and change
        if isinstance(left, str):
            left = Var(left)
        if isinstance(left, (float, int)):
            left = Num(left)
        if isinstance(right, str):
            right = Var(right)
        if isinstance(right, (float, int)):
            right = Num(right)

        self.left = left
        self.right = right
        self.Op = Op

    def eval_Op(self, left, right):
        if self.Op == "Add":
            return left + right
        elif self.Op == "Sub":
            return left - right
        elif self.Op == "Mul":
            return left * right
        else:
            return left / right

    def precedence(self):
        # P-E-MD-AS
        if self.Op in {"Sub", "Add"}:
            return 1
        if self.Op in {"Mul", "Div"}:
            return 2
        return 0

    def evaluate(self, mapping):
        """mapping is the dictionary
        of variables to values"""
        # the mapping will only contain the values of the variables
        left, right = self.left, self.right
        left_eval = left.evaluate(mapping)
        right_eval = right.evaluate(mapping)
        return self.eval_Op(left_eval, right_eval)

    def __eq__(self, other):
        if self.Op != other.Op:
            return False

        # For commutative operations, allow swapped operands
        if self.Op in {"Add", "Mul"}:
            return (self.left == other.left and self.right == other.right) or (
                self.left == other.right and self.right == other.left
            )

        # For non-commutative operations (Sub, Div), require exact match
        return self.left == other.left and self.right == other.right

    def __repr__(self):
        return f"{self.Op}({self.left.__repr__()}, {self.right.__repr__()})"

    def __str__(self):
        op_syms = {"Add": "+", "Sub": "-", "Mul": "*", "Div": "/"}
        sym = f" {op_syms[self.Op]} "

        left, right = self.left, self.right
        self_p = self.precedence()
        left_p, right_p = left.precedence(), right.precedence()

        # Change Left String
        left_str = f"({left})" if left_p < self_p else str(left)

        # Change Right String
        if right_p < self_p or (self.Op in {"Sub", "Div"} and right_p == self_p):
            right_str = f"({right})"
        else:
            right_str = str(right)

        return f"{left_str}{sym}{right_str}"


class Add(BinOp):
    """Class to represent Addition
    Binary operation"""

    def __init__(self, left, right):
        BinOp.__init__(self, left, right, "Add")

    def deriv(self, variable):
        return self.left.deriv(variable) + self.right.deriv(variable)

    def simplify(self):
        l, r = self.left, self.right
        ls = l.simplify()
        rs = r.simplify()
        #Simplification_cases
        if isinstance(ls, Num):
            if isinstance(rs, Num):
                return Num(self.eval_Op(ls.n, rs.n))
            
            if ls == Num(0):
                return rs
            
        if isinstance(rs, Num):
            if rs == Num(0):
                return ls    
        
        #Recursive
        return self.eval_Op(ls, rs)

class Sub(BinOp):
    """Class to represent Subtraction
    Binary operation"""

    def __init__(self, left, right):
        BinOp.__init__(self, left, right, "Sub")

    def deriv(self, variable):
        return self.left.deriv(variable) - self.right.deriv(variable)
    
    def simplify(self):
        l, r = self.left, self.right
        ls = l.simplify()
        rs = r.simplify()
        #Simplification_cases
        if isinstance(ls, Num):
            if isinstance(rs, Num):
                return Num(self.eval_Op(ls.n, rs.n))
                        
        if isinstance(rs, Num):
            if rs == Num(0):
                return ls    
        
        #Recursive
        return self.eval_Op(ls, rs)

class Mul(BinOp):
    """Class to represent Multiplication
    binary operation"""

    def __init__(self, left, right):
        BinOp.__init__(self, left, right, "Mul")

    def deriv(self, variable):
        return ((self.left) * self.right.deriv(variable)) + (
            self.right * self.left.deriv(variable)
        )

    def simplify(self):
        l, r = self.left, self.right
        ls = l.simplify()
        rs = r.simplify()
        #Simplification_cases
        if isinstance(ls, Num):
            if isinstance(rs, Num):
                return Num(self.eval_Op(ls.n, rs.n))
            
            if ls == Num(0):
                return Num(0)
            if ls == Num(1):
                return rs
            
        if isinstance(rs, Num):
            if rs == Num(0):
                return Num(0)  
            if rs == Num(1):
                return ls
        
        #Recursive
        return self.eval_Op(ls, rs)



class Div(BinOp):
    """Class to represent Division Binary Operation"""

    def __init__(self, left, right):
        BinOp.__init__(self, left, right, "Div")

    def deriv(self, variable):
        numerator = (self.right * self.left.deriv(variable)) - (
            self.left * self.right.deriv(variable)
        )
        denominator = self.right * self.right
        return numerator / denominator

    def simplify(self):
        l, r = self.left, self.right
        ls = l.simplify()
        rs = r.simplify()
        #Simplification_cases
        if isinstance(ls, Num):
            if isinstance(rs, Num):
                return Num(self.eval_Op(ls.n, rs.n))
            
            if ls == Num(0):
                return Num(0)
            
        if isinstance(rs, Num):
            if rs == Num(1):
                return ls
        
        #Recursive
        return self.eval_Op(ls, rs)

class SymbolicEvaluationError(Exception):
    """
    An expression indicating that something has gone wrong when evaluating a
    symbolic algebra expression.
    """

    pass


def make_expression(expression, flush=False):
    """Function that takes in the expression string and returns
    the expression interms of the expression class"""
    tokens = tokenize(expression)
    if flush:
        print(f"Tokens: {tokens}", flush=True)
    expression = parse(tokens, flush)
    return expression


def parse(tokens, flush=False):
    """Parses the tokens list into an expression tree,
    assuming parentheses are always present."""
    operators = {"+": Add, "-": Sub, "*": Mul, "/": Div}
    start = "("
    end = ")"

    def recursive_parse(index):
        """Recursively parses the tokens to build the expression."""
        token = tokens[index]
        if token == start:
            # Skip the start bracket
            left_exp, index = recursive_parse(index + 1)

            if flush:
                print(f"left: {left_exp}")

            Op = tokens[index]
            right_exp, index = recursive_parse(index + 1)
            if flush:
                print(f"right:{right_exp}")

            if tokens[index] is not end:
                raise ValueError("String Expression is not properly Bracketed")

            index += 1  # skip the end bracket

            out = operators[Op](left_exp, right_exp)
            if flush:
                print(f"out: {out}")
            return out, index

        # variables
        elif token.isalpha():
            return Var(token), index + 1

        # numbers
        else:
            return Num(float(token)), index + 1

    parsed_expression, _ = recursive_parse(0)
    return parsed_expression


def tokenize(expression):
    """Helper function that takes in a string of expression
    and tokenises accordingly, to be fed into the parse function"""
    special_ops = {"+", "-", "*", "/", "(", ")"}
    num_chars = set("0123456789.")
    out_tokens = []
    curr_char = ""
    prev_token = None

    for char in expression:

        if char == " ":
            continue

        if char in num_chars:
            curr_char += char

        elif char in special_ops:
            if char == "-" and prev_token in {None, "(", "+", "-", "*", "/"}:
                curr_char += char  # start of negative number
            else:
                if curr_char:
                    out_tokens.append(curr_char)
                    prev_token = curr_char
                    curr_char = ""
                out_tokens.append(char)
                prev_token = char

        else:
            # variable/letter
            if curr_char:
                out_tokens.append(curr_char)
                prev_token = curr_char
                curr_char = ""
            out_tokens.append(char)
            prev_token = char

        prev_token = char

    if curr_char:
        out_tokens.append(curr_char)

    return out_tokens


def test_make_expression():
    """Custom test function for make_expression
    function"""
    string_expressions = ["((x*x) + (y*y))", "(2 - (y/z)))", "(p - (q * r))"]

    expected_expressions = [
        Add(Mul(Var("x"), Var("x")), Mul(Var("y"), Var("y"))),
        Sub(Num(2.0), Div(Var("y"), Var("z"))),
        Sub(Var("p"), Mul(Var("q"), Var("r"))),
    ]

    for str_exp, exp_exp in zip(string_expressions, expected_expressions):
        result = make_expression(str_exp)
        assert str(result) == str(
            exp_exp
        ), f"Resultant expression: {str(result)}, \
                                        Expected expression: {str(exp_exp)}"

    print("All Test Passed")


if __name__ == "__main__":
    pass
    # Testing the function
    # token1 = tokenize('6.1010')
    # print(token1)
    # tokens = tokenize("(x * (2 + 3))")
    # print(tokens)
    # exp = parse(tokens)
    # y = make_expression("(x * (2 + 3))")
    # print(y)
    # string_expression = ['((x*x) + (y*y))',
    #         '(2 - (y/z)))',
    #         '(p - (q * r))']

    # expected_expression = [
    #                 Add(Mul(Var('x'), Var('x')), Mul(Var('y'), Var('y'))),
    #                 Sub(Num(2), Div(Var('y'), Var('z'))),
    #                 Sub(Var('p'), Mul(Var('q'), Var('r')))
    #                 ]
    # result1 = make_expression(string_expression[2])
    # print(result1)
    # print(expected_expression[2])
    test_make_expression()
