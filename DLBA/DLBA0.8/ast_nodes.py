# ast_nodes.py - DLBA AST nodes (v0.8)
class Number:
    def __init__(self, value):
        self.value = value
        self.lineno = None
        self.filename = None
        self.col = None

class String:
    def __init__(self, value):
        self.value = value
        self.lineno = None
        self.filename = None
        self.col = None

class Boolean:
    def __init__(self, value):
        self.value = value
        self.lineno = None
        self.filename = None
        self.col = None

class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
        self.lineno = getattr(left, 'lineno', None)
        self.filename = getattr(left, 'filename', None)
        self.col = getattr(left, 'col', None)

class UnaryOp:
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand
        self.lineno = getattr(operand, 'lineno', None)
        self.filename = getattr(operand, 'filename', None)
        self.col = getattr(operand, 'col', None)

class Var:
    def __init__(self, name):
        self.name = name
        self.lineno = None
        self.filename = None
        self.col = None

class Assign:
    def __init__(self, name, expr, declare=False):
        self.name = name
        self.expr = expr
        self.declare = declare
        self.lineno = getattr(expr, 'lineno', None)
        self.filename = getattr(expr, 'filename', None)
        self.col = getattr(expr, 'col', None)

class Print:
    def __init__(self, expr):
        self.expr = expr
        self.lineno = getattr(expr, 'lineno', None)
        self.filename = getattr(expr, 'filename', None)
        self.col = getattr(expr, 'col', None)

class If:
    def __init__(self, condition, then_branch, elif_branches=None, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.elif_branches = elif_branches or []
        self.else_branch = else_branch
        self.lineno = getattr(condition, 'lineno', None)
        self.filename = getattr(condition, 'filename', None)
        self.col = getattr(condition, 'col', None)

class While:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
        self.lineno = getattr(condition, 'lineno', None)
        self.filename = getattr(condition, 'filename', None)
        self.col = getattr(condition, 'col', None)

class FunctionDef:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body
        self.lineno = None
        self.filename = None
        self.col = None

class Return:
    def __init__(self, expr):
        self.expr = expr
        self.lineno = getattr(expr, 'lineno', None) if expr is not None else None
        self.filename = getattr(expr, 'filename', None) if expr is not None else None
        self.col = getattr(expr, 'col', None) if expr is not None else None

class Call:
    def __init__(self, callee, args):
        self.callee = callee
        self.args = args
        self.lineno = getattr(callee, 'lineno', None)
        self.filename = getattr(callee, 'filename', None)
        self.col = getattr(callee, 'col', None)

class Import:
    def __init__(self, path, as_name=None, names=None):
        self.path = path
        self.as_name = as_name
        self.names = names
        self.lineno = None
        self.filename = None
        self.col = None

class ModuleAccess:
    def __init__(self, obj, member):
        self.obj = obj
        self.member = member
        self.lineno = getattr(obj, 'lineno', None)
        self.filename = getattr(obj, 'filename', None)
        self.col = getattr(obj, 'col', None)

class ListLiteral:
    def __init__(self, elements):
        self.elements = elements
        self.lineno = getattr(elements[0], 'lineno', None) if elements else None
        self.filename = getattr(elements[0], 'filename', None) if elements else None
        self.col = getattr(elements[0], 'col', None) if elements else None

class DictLiteral:
    def __init__(self, pairs):
        self.pairs = pairs  # list of (key_node, value_node)
        self.lineno = getattr(pairs[0][0], 'lineno', None) if pairs else None
        self.filename = getattr(pairs[0][0], 'filename', None) if pairs else None
        self.col = getattr(pairs[0][0], 'col', None) if pairs else None

class Index:
    def __init__(self, target, index_expr):
        self.target = target
        self.index_expr = index_expr  # could be Number/Var or Slice node
        self.lineno = getattr(target, 'lineno', None)
        self.filename = getattr(target, 'filename', None)
        self.col = getattr(target, 'col', None)

class Slice:
    def __init__(self, start, stop):
        self.start = start  # can be None
        self.stop = stop    # can be None
        self.lineno = getattr(start, 'lineno', None) if start else getattr(stop, 'lineno', None)
        self.filename = getattr(start, 'filename', None) if start else getattr(stop, 'filename', None)
        self.col = getattr(start, 'col', None) if start else getattr(stop, 'col', None)
