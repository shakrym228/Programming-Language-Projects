from parser import Number, Identifier, BinaryOp, Assignment, Print

class Environment:
    def __init__(self):
        self.vars = {}

    def set_(self, name, value):
        self.vars[name] = value

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        raise Exception(f"متغیر '{name}' تعریف نشده")

def eval_node(node, env):
    if isinstance(node, Number):
        return node.value
    elif isinstance(node, Identifier):
        return env.get(node.name)
    elif isinstance(node, BinaryOp):
        left = eval_node(node.left, env)
        right = eval_node(node.right, env)
        if node.op == '+':
            return left + right
        elif node.op == '-':
            return left - right
        elif node.op == '*':
            return left * right
        elif node.op == '/':
            return left // right
        else:
            raise Exception(f"عملگر ناشناخته: {node.op}")
    else:
        raise Exception("نوع گره ناشناخته در eval_node")

def exec_statement(stmt, env):
    if isinstance(stmt, Assignment):
        value = eval_node(stmt.expr, env)
        env.set_(stmt.name, value)
    elif isinstance(stmt, Print):
        value = eval_node(stmt.expr, env)
        print(value)

def interpret(program):
    env = Environment()
    for stmt in program:
        exec_statement(stmt, env)