# ast_nodes.py
# AST node definitions for DLBA v0.4

class Number:
    def __init__(self, value):
        self.value = value  # int or float

class String:
    def __init__(self, value):
        self.value = value  # python str

class Boolean:
    def __init__(self, value):
        self.value = value  # True / False

class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnaryOp:
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

class Var:
    def __init__(self, name):
        self.name = name

class Assign:
    def __init__(self, name, expr, declare=False):
        # declare=True when `let` is used; False for reassignment
        self.name = name
        self.expr = expr
        self.declare = declare

class Print:
    def __init__(self, expr):
        self.expr = expr

class If:
    def __init__(self, condition, then_branch, elif_branches=None, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.elif_branches = elif_branches or []  # list of (cond, branch)
        self.else_branch = else_branch

class While:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class FunctionDef:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params  # list of parameter names
        self.body = body      # list of statements

class Return:
    def __init__(self, expr):
        self.expr = expr

class Call:
    def __init__(self, callee, args):
        # callee: Var or expression that evaluates to function value
        self.callee = callee
        self.args = args  # list of expressions
