# Lexer####################################################################
from typing import Self
import ply
import ply.lex as lex
import math
import random

# constants
PI = math.pi
E = math.e

# List of token names.
tokens = (
    "NUMBER",
    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
    "LPAREN",
    "RPAREN",
    "PI",
    "E",
    "PRINT",
    "SQRT",
    "SIN",
    "COS",
    "EXP",
    "LOG",
    "RAND",
    "COMMA",
)

# Regular expression rules
t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_DIVIDE = r"/"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_PI = r"PI"
t_E = r"E"
t_SQRT = r"sqrt"
t_SIN = r"sin"
t_COS = r"cos"
t_EXP = r"exp"
t_LOG = r"log"
t_RAND = r"rand"
t_COMMA = r","
t_PRINT = r"print"

# A string containing ignored characters (spaces and tabs)
t_ignore = " \t"


# A regular expression rule with some action code
def t_NUMBER(t):
    r"\d+"
    t.value = int(t.value)
    return t


# Define a rule so we can track line numbers
def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()

###############################################################################################
###############################################################################################

# Parser########################################################################################


# base class
class Node:

    def check(self):
        pass

    def infer_type(self):
        pass

    def eval(self):
        pass


# Operations Classes (binary, unary,etc)
class BinOp(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def check(
        self,
    ):  # most be modified to works with all binary operators, now only works with '+', '-', '*', '/'
        # Check the operands
        self.left.check()
        self.right.check()

        # Check the operator
        if self.op not in ["+", "-", "*", "/"]:
            raise TypeError(f"Invalid operator: {self.op}")

        # Infer the types of the operands
        left_type = self.left.infer_type()
        right_type = self.right.infer_type()

        # Check that the types are compatible
        if left_type != right_type:
            raise TypeError(f"Type mismatch: {left_type} {self.op} {right_type}")

        # Check that the types are valid for the operation
        if left_type != "number":
            raise TypeError(f"Invalid type for operation: {left_type}")

    def infer_type(self):
        # Infer the types of the operands
        left_type = self.left.infer_type()

        # The type of a binary operation is the type of its operands
        return left_type

    def eval(self):
        if self.op == "+":
            return self.left.eval() + self.right.eval()
        elif self.op == "-":
            return self.left.eval() - self.right.eval()
        elif self.op == "*":
            return self.left.eval() * self.right.eval()
        elif self.op == "/":
            right = self.right.eval()
            if right == 0:
                raise ZeroDivisionError("division by zero")
            return self.left.eval() / right


class UnaryOp(Node):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

    def check(
        self,
    ):  # most be modified to works with all unary operators, now only works with '-' and only "-"
        # Check the operand
        self.operand.check()

        # Check the operator
        if self.op != "-":
            raise TypeError(f"Invalid operator: {self.op}")
        if self.operand.infer_type() != "number":
            raise TypeError(f"Invalid type for operation: {self.operand.infer_type()}")

    def infer_type(self):
        # Infer the type of the operand
        operand_type = self.operand.infer_type()

        # The type of a unary operation is the type of its operand
        return operand_type

    def eval(self):
        if self.op == "-":
            return -self.operand.eval()


# number class
class Num(Node):
    def __init__(self, value):
        if isinstance(value, (int, float)):
            self.value = float(value)
        else:
            self.value = value

    def check(self):
        # Check that the value is a number
        if not isinstance(self.value, (float)):
            raise TypeError(f"Invalid number: {self.value}")

    def infer_type(self):
        # The type of a number is 'num'
        return "number"

    def eval(self):
        return self.value


# constants classes
class Pi(Node):
    def check(self):
        pass

    def infer_type(self):
        return "number"

    def eval(self):
        return PI


class E(Node):
    def check(self):
        pass

    def infer_type(self):
        return "number"

    def eval(self):
        return E


# built-in functions classes
class Print(
    Node
):  # most be modified to work with all literals, now only works with numbers, missing strings and booleans
    def __init__(self, value):
        self.value = value

    def check(self):
        self.value.check()

    def infer_type(self):
        return "void"

    def eval(self):
        print(self.value.eval())


class Sqrt(Node):
    def __init__(self, value):
        self.value = value

    def check(self):
        self.value.check()
        if self.value.infer_type() != "number":
            raise TypeError(f"Invalid type for operation: {self.value.infer_type()}")
        if self.value.eval() < 0:
            raise ValueError("sqrt of a negative number")

    def infer_type(self):
        return "number"

    def eval(self):
        return math.sqrt(self.value.eval())


class Sin(Node):
    def __init__(self, value):
        self.value = value

    def check(self):
        self.value.check()
        if self.value.infer_type() != "number":
            raise TypeError(f"Invalid type for operation: {self.value.infer_type()}")

    def infer_type(self):
        return "number"

    def eval(self):
        return math.sin(self.value.eval())


class Cos(Node):
    def __init__(self, value):
        self.value = value

    def check(self):
        self.value.check()
        if self.value.infer_type() != "number":
            raise TypeError(f"Invalid type for operation: {self.value.infer_type()}")

    def infer_type(self):
        return "number"

    def eval(self):
        return math.cos(self.value.eval())


class Exp(Node):
    def __init__(self, value):
        self.value = value

    def check(self):
        self.value.check()
        if self.value.infer_type() != "number":
            raise TypeError(f"Invalid type for operation: {self.value.infer_type()}")

    def infer_type(self):
        return "number"

    def eval(self):
        return math.exp(self.value.eval())


class Log(Node):
    def __init__(self, value, base):
        self.base = base
        self.value = value

    def check(self):
        self.base.check()
        self.value.check()
        if self.base.infer_type() != "number":
            raise TypeError(
                f"Invalid type for operation in base of log: {self.base.infer_type()}"
            )
        if self.value.infer_type() != "number":
            raise TypeError(
                f"Invalid type for operation in argument of log: {self.value.infer_type()}"
            )

    def infer_type(self):
        return "number"

    def eval(self):
        return math.log(self.base.eval(), self.value.eval())


class Rand(Node):
    def check(self):
        pass

    def infer_type(self):
        return "number"

    def eval(self):
        return random.uniform(0, 1)


import ply.yacc as yacc

# precedence rules for the arithmetic operators
precedence = (
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE"),
    ("right", "LPAREN", "RPAREN"),
    ("nonassoc", "UMINUS"),
)

# dictionary of names (for storing variables)
names = {}


# defining the grammatical
def p_statement_expr(p):
    "statement : expression"
    p[0] = p[1]


def p_expression_group(p):
    "expression : LPAREN expression RPAREN"
    p[0] = p[2]


def p_expression_binop(p):
    """expression : expression PLUS expression
    | expression MINUS expression
    | expression TIMES expression
    | expression DIVIDE expression"""
    p[0] = BinOp(left=p[1], op=p[2], right=p[3])


def p_expression_uminus(p):
    "expression : MINUS expression %prec UMINUS"  # no se que significa el %prec UMINUS ese,recomiendo ignorarlo hasta q se parta algo
    p[0] = UnaryOp(op=p[1], operand=p[2])


def p_expression_number(p):
    "expression : NUMBER"
    p[0] = Num(p[1])


# constants
def p_expression_pi(p):
    "expression : PI"
    p[0] = Pi()


def p_expression_e(p):
    "expression : E"
    p[0] = E()


# Built-in functions
def p_expression_print(p):
    "expression : PRINT LPAREN expression RPAREN"
    p[0] = Print(p[3])


def p_expression_sqrt(p):
    "expression : SQRT LPAREN expression RPAREN"
    p[0] = Sqrt(p[3])


def p_expression_sin(p):
    "expression : SIN LPAREN expression RPAREN"
    p[0] = Sin(p[3])


def p_expression_cos(p):
    "expression : COS LPAREN expression RPAREN"
    p[0] = Cos(p[3])


def p_expression_exp(p):
    "expression : EXP LPAREN expression RPAREN"
    p[0] = Exp(p[3])


def p_expression_log(p):
    "expression : LOG LPAREN expression COMMA expression RPAREN"
    p[0] = Log(p[3], p[5])


def p_expression_rand(p):
    "expression : RAND LPAREN RPAREN"
    p[0] = Rand()


def p_error(p):
    if p:
        print(f"Syntax error at {p.value}")
    else:
        print("Syntax error at EOF")


# Generate C code from AST
def generate_c_code(node):
    if isinstance(node, BinOp):
        return f"({generate_c_code(node.left)} {node.op} {generate_c_code(node.right)})"
    elif isinstance(node, Num):
        return str(node.value)
    elif isinstance(node, UnaryOp):
        return f"{node.op}{generate_c_code(node.operand)}"
    elif isinstance(node, Print):
        return f'printf("%f\\n", {generate_c_code(node.value)})'
    elif isinstance(node, Pi):
        return "M_PI"
    elif isinstance(node, E):
        return "M_E"
    elif isinstance(node, Sqrt):
        return f"sqrt({generate_c_code(node.value)})"
    elif isinstance(node, Sin):
        return f"sin({generate_c_code(node.value)})"
    elif isinstance(node, Cos):
        return f"cos({generate_c_code(node.value)})"
    elif isinstance(node, Exp):
        return f"exp({generate_c_code(node.value)})"
    elif isinstance(node, Log):
        return f"(log({generate_c_code(node.base)}) / log({generate_c_code(node.value)}))"  # logaritmo se hace asi pq C no admite log de a en base b
    elif isinstance(node, Rand):
        return "((double) rand() / (RAND_MAX))"
    else:
        raise TypeError(f"Unknown node {node}")


# create output.c file with the code transformed
def write_c_code_to_file(ast, filename):
    c_code = generate_c_code(ast)
    with open(filename, "w") as f:
        f.write("#include <stdio.h>\n")
        f.write("#include <math.h>\n")
        f.write("#include <stdlib.h>\n\n")
        f.write("int main() {\n")
        f.write(f"    {c_code};\n")
        f.write("    return 0;\n")
        f.write("}\n")


parser = yacc.yacc()

# Generate AST
hulk_code = "print(rand())"

ast = parser.parse(hulk_code)
# semantic and type check
ast.check()

# evaluate the AST in python code before generating the c code
ast.eval()


# Generate C code
write_c_code_to_file(ast, "output.c")
