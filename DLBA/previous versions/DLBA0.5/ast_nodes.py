# ast_nodes.py - DLBA v0.5 AST node definitions

class Number:
    def __init__(self, value):
        self.value = value
        self.lineno = None
        self.filename = None

class String:
    def __init__(self, value):
        self.value = value
        self.lineno = None
        self.filename = None

class Boolean:
    def __init__(self, value):
        self.value = value
        self.lineno = None
        self.filename = None

class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
        self.lineno = getattr(left, 'lineno', None)
        self.filename = getattr(left, 'filename', None)

class UnaryOp:
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand
        self.lineno = getattr(operand, 'lineno', None)
        self.filename = getattr(operand, 'filename', None)

class Var:
    def __init__(self, name):
        self.name = name
        self.lineno = None
        self.filename = None

class Assign:
    def __init__(self, name, expr, declare=False):
        self.name = name
        self.expr = expr
        self.declare = declare
        self.lineno = getattr(expr, 'lineno', None)
        self.filename = getattr(expr, 'filename', None)

class Print:
    def __init__(self, expr):
        self.expr = expr
        self.lineno = getattr(expr, 'lineno', None)
        self.filename = getattr(expr, 'filename', None)

class If:
    def __init__(self, condition, then_branch, elif_branches=None, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.elif_branches = elif_branches or []
        self.else_branch = else_branch
        self.lineno = getattr(condition, 'lineno', None)
        self.filename = getattr(condition, 'filename', None)

class While:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
        self.lineno = getattr(condition, 'lineno', None)
        self.filename = getattr(condition, 'filename', None)

class FunctionDef:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body
        self.lineno = None
        self.filename = None

class Return:
    def __init__(self, expr):
        self.expr = expr
        self.lineno = getattr(expr, 'lineno', None) if expr is not None else None
        self.filename = getattr(expr, 'filename', None) if expr is not None else None

class Call:
    def __init__(self, callee, args):
        self.callee = callee
        self.args = args
        # lineno from callee or first arg
        self.lineno = getattr(callee, 'lineno', None)
        self.filename = getattr(callee, 'filename', None)

class Import:
    def __init__(self, path):
        self.path = path
        self.lineno = None
        self.filename = None
