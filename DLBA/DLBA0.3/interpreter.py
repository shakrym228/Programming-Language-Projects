from ast_nodes import *

# interpreter functions expect an Environment instance (env)

def interpret(statements, env):
    for stmt in statements:
        execute(stmt, env)

def execute(node, env):
    if isinstance(node, Assign):
        value = evaluate(node.expr, env)
        if node.declare:
            # let - always create/overwrite
            env.set(node.name, value)
        else:
            # plain assignment - variable must exist
            if env.exists(node.name):
                env.set(node.name, value)
            else:
                raise Exception(f"Undefined variable '{node.name}'. Use 'let' to declare it first.")
    elif isinstance(node, Print):
        val = evaluate(node.expr, env)
        print(val)
    elif isinstance(node, If):
        cond = evaluate(node.condition, env)
        if cond:
            for s in node.then_branch:
                execute(s, env)
        else:
            executed = False
            for (econd, ebranch) in node.elif_branches:
                if evaluate(econd, env):
                    for s in ebranch:
                        execute(s, env)
                    executed = True
                    break
            if not executed and node.else_branch:
                for s in node.else_branch:
                    execute(s, env)
    elif isinstance(node, While):
        # loop until condition is false
        while evaluate(node.condition, env):
            for s in node.body:
                execute(s, env)
    else:
        raise Exception(f"Unknown statement type: {type(node)}")

def truthy(value):
    # define DLBA truthiness: False/None/0/0.0/"" are falsey otherwise true
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return len(value) != 0
    return True

def evaluate(node, env):
    if isinstance(node, Number):
        return node.value
    if isinstance(node, String):
        return node.value
    if isinstance(node, Boolean):
        return node.value
    if isinstance(node, Var):
        return env.get(node.name)
    if isinstance(node, UnaryOp):
        val = evaluate(node.operand, env)
        if node.op == '!':
            return not truthy(val)
        if node.op == '-':
            if isinstance(val, (int, float)):
                return -val
            raise Exception("Unary '-' applied to non-number")
        raise Exception(f"Unknown unary operator: {node.op}")
    if isinstance(node, BinOp):
        op = node.op
        # logical OR (short-circuit)
        if op == '||':
            left = evaluate(node.left, env)
            if truthy(left):
                return True
            right = evaluate(node.right, env)
            return truthy(right)
        # logical AND (short-circuit)
        if op == '&&':
            left = evaluate(node.left, env)
            if not truthy(left):
                return False
            right = evaluate(node.right, env)
            return truthy(right)

        left = evaluate(node.left, env)
        right = evaluate(node.right, env)

        # arithmetic + string concat
        if op == '+':
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            return left + right
        if op == '-':
            return left - right
        if op == '*':
            return left * right
        if op == '/':
            return left / right  # true division (float)
        # comparisons
        if op == '<': return left < right
        if op == '>': return left > right
        if op == '<=': return left <= right
        if op == '>=': return left >= right
        if op == '==': return left == right
        if op == '!=': return left != right

        raise Exception(f"Unknown binary operator: {op}")

    raise Exception(f"Cannot evaluate node of type: {type(node)}")
