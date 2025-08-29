from ast_nodes import *

class Environment:
    def __init__(self):
        self.variables = {}

    def get(self, name):
        if name in self.variables:
            return self.variables[name]
        else:
            raise Exception(f"متغیر تعریف نشده: {name}")

    def set_(self, name, value):
        self.variables[name] = value

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
        elif node.op == '<':
            return left < right
        elif node.op == '>':
            return left > right
        elif node.op == '<=':
            return left <= right
        elif node.op == '>=':
            return left >= right
        elif node.op == '==':
            return left == right
        elif node.op == '!=':
            return left != right
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
    elif isinstance(stmt, IfStatement):
        condition = eval_node(stmt.condition, env)
        branch = stmt.then_branch if condition else stmt.else_branch
        for s in branch:
            exec_statement(s, env)