from ast_nodes import *
# interpreter expects an Environment instance (from env.py)

def interpret(statements, env):
    for stmt in statements:
        execute(stmt, env)

def execute(node, env):
    # Assign node: declare=True -> 'let', declare=False -> plain assignment (reassignment)
    if isinstance(node, Assign):
        value = evaluate(node.expr, env)
        if node.declare:
            # let declaration (always set)
            env.set(node.name, value)
        else:
            # plain assignment: require that variable already exists
            if env.exists(node.name):
                env.set(node.name, value)
            else:
                raise Exception(f"Undefined variable '{node.name}'. Use 'let' to declare it before assignment.")
    elif isinstance(node, Print):
        value = evaluate(node.expr, env)
        print(value)
    elif isinstance(node, If):
        cond = evaluate(node.condition, env)
        if cond:
            for s in node.then_branch:
                execute(s, env)
        elif node.else_branch:
            for s in node.else_branch:
                execute(s, env)
    elif isinstance(node, While):
        # evaluate each loop iteration
        while evaluate(node.condition, env):
            for s in node.body:
                execute(s, env)
    else:
        raise Exception(f"Unknown statement type: {type(node)}")

def evaluate(node, env):
    if isinstance(node, Number):
        return node.value
    elif isinstance(node, Boolean):
        return node.value
    elif isinstance(node, Var):
        return env.get(node.name)
    elif isinstance(node, BinOp):
        left = evaluate(node.left, env)
        right = evaluate(node.right, env)
        op = node.op
        if op == '+': return left + right
        if op == '-': return left - right
        if op == '*': return left * right
        if op == '/': return left // right
        if op == '<': return left < right
        if op == '>': return left > right
        if op == '<=': return left <= right
        if op == '>=': return left >= right
        if op == '==': return left == right
        if op == '!=': return left != right
        raise Exception(f"Unknown operator: {op}")
    else:
        raise Exception(f"Cannot evaluate node of type: {type(node)}")
