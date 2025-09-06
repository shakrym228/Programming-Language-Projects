# AST node definitions for DLBA v0.2

class Number:
    def __init__(self, value):
        self.value = value

class Boolean:
    def __init__(self, value):
        self.value = value

class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Var:
    def __init__(self, name):
        self.name = name

class Assign:
    def __init__(self, name, expr, declare=False):
        # declare=True for "let" declarations, declare=False for plain assignment (x = ...)
        self.name = name
        self.expr = expr
        self.declare = declare

class Print:
    def __init__(self, expr):
        self.expr = expr

class If:
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch  # list of statements
        self.else_branch = else_branch  # list of statements or None

class While:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body  # list of statements