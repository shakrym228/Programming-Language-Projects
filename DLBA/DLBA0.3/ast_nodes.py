# AST nodes for DLBA v0.3

class Number:
    def __init__(self, value):
        self.value = value  # int or float

class String:
    def __init__(self, value):
        self.value = value  # Python str

class Boolean:
    def __init__(self, value):
        self.value = value  # True/False

class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnaryOp:
    def __init__(self, op, operand):
        self.op = op  # '!' or '-'
        self.operand = operand

class Var:
    def __init__(self, name):
        self.name = name

class Assign:
    def __init__(self, name, expr, declare=False):
        self.name = name
        self.expr = expr
        self.declare = declare  # True when "let" used

class Print:
    def __init__(self, expr):
        self.expr = expr

class If:
    def __init__(self, condition, then_branch, elif_branches=None, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch            # list of statements
        self.elif_branches = elif_branches or []  # list of (cond, branch)
        self.else_branch = else_branch            # list of statements or None

class While:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body  # list of statements
