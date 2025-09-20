# interpreter.py
from ast_nodes import *
from env import Environment

# Custom exception to handle returns
class ReturnException(Exception):
    def __init__(self, value):
        super().__init__("Function returned")
        self.value = value

# A function value to capture params, body and closure (lexical environment)
class FunctionValue:
    def __init__(self, params, body, closure_env):
        self.params = params
        self.body = body
        self.closure_env = closure_env

def interpret(statements, env):
    for stmt in statements:
        execute(stmt, env)

def execute(node, env):
    if isinstance(node, Assign):
        val = evaluate(node.expr, env)
        if node.declare:
            env.declare(node.name, val)
        else:
            if env.exists(node.name):
                env.set(node.name, val)
            else:
                raise Exception(f"Undefined variable '{node.name}'. Use 'let' to declare it first.")
        return None

    if isinstance(node, FunctionDef):
        # create function value and store in current scope
        fv = FunctionValue(node.params, node.body, env)
        env.declare(node.name, fv)
        return None

    if isinstance(node, Return):
        val = evaluate(node.expr, env) if node.expr is not None else None
        raise ReturnException(val)

    if isinstance(node, Print):
        val = evaluate(node.expr, env)
        print(val)
        return None

    if isinstance(node, If):
        cond_val = evaluate(node.condition, env)
        if truthy(cond_val):
            for s in node.then_branch:
                execute(s, env)
            return None
        for (econd, ebranch) in node.elif_branches:
            if truthy(evaluate(econd, env)):
                for s in ebranch:
                    execute(s, env)
                return None
        if node.else_branch:
            for s in node.else_branch:
                execute(s, env)
        return None

    if isinstance(node, While):
        while truthy(evaluate(node.condition, env)):
            for s in node.body:
                execute(s, env)
        return None

    if isinstance(node, Call):
        # evaluate callee (should be function)
        callee = evaluate(node.callee, env)
        if not isinstance(callee, FunctionValue):
            raise Exception("Attempt to call a non-function value")
        # evaluate args
        arg_vals = [evaluate(a, env) for a in node.args]
        # create new env with closure as parent (lexical scoping)
        call_env = Environment(parent=callee.closure_env)
        # bind parameters
        for i, pname in enumerate(callee.params):
            pval = arg_vals[i] if i < len(arg_vals) else None
            call_env.declare(pname, pval)
        # execute function body, catch return
        try:
            for s in callee.body:
                execute(s, call_env)
        except ReturnException as re:
            return re.value
        return None

    raise Exception(f"Unknown statement type: {type(node)}")

def truthy(value):
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
        # logical OR short-circuit
        if op == '||':
            left = evaluate(node.left, env)
            if truthy(left):
                return True
            right = evaluate(node.right, env)
            return truthy(right)
        # logical AND short-circuit
        if op == '&&':
            left = evaluate(node.left, env)
            if not truthy(left):
                return False
            right = evaluate(node.right, env)
            return truthy(right)

        left = evaluate(node.left, env)
        right = evaluate(node.right, env)

        # arithmetic / concat
        if op == '+':
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            return left + right
        if op == '-':
            return left - right
        if op == '*':
            return left * right
        if op == '/':
            return left / right
        if op == '%':
            return left % right

        # comparisons
        if op == '<': return left < right
        if op == '>': return left > right
        if op == '<=': return left <= right
        if op == '>=': return left >= right
        if op == '==': return left == right
        if op == '!=': return left != right

        raise Exception(f"Unknown binary operator: {op}")

    if isinstance(node, Call):
        # enable calling evaluate(call_node) as expression context
        return execute(node, env)

    raise Exception(f"Cannot evaluate node of type: {type(node)}")
