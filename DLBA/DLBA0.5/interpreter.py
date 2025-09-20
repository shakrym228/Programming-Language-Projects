# interpreter.py - modules + call-stack + better error info
import os
from ast_nodes import *
from env import Environment

# Interpreter-level module cache and loading status
_loaded_modules = {}   # abs_path -> module_env
_loading = set()       # abs_paths currently loading (detect cycles)

# call stack for runtime tracing - list of frames (func_name, filename, lineno)
_call_stack = []

def get_call_stack():
    return list(_call_stack)

# FunctionValue and ReturnException
class ReturnException(Exception):
    def __init__(self, value):
        super().__init__("Function returned")
        self.value = value

class FunctionValue:
    def __init__(self, params, body, closure_env, name=None, def_filename=None, def_lineno=None):
        self.params = params
        self.body = body
        self.closure_env = closure_env
        self.name = name
        self.def_filename = def_filename
        self.def_lineno = def_lineno

def interpret(statements, env, current_filename=None):
    # execute top-level statements
    for stmt in statements:
        execute(stmt, env)

def execute(node, env):
    try:
        if isinstance(node, Assign):
            val = evaluate(node.expr, env)
            if node.declare:
                env.declare(node.name, val)
            else:
                if env.exists(node.name):
                    env.set(node.name, val)
                else:
                    raise Exception(f"Undefined variable '{node.name}'. Use 'let' to declare it first. at {node.filename}:{node.lineno}")
            return None

        if isinstance(node, FunctionDef):
            # create function value and store in current scope
            fv = FunctionValue(node.params, node.body, env, name=node.name, def_filename=node.filename, def_lineno=node.lineno)
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
            if truthy(evaluate(node.condition, env)):
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
            # call expression used as statement
            result = _call_function_node(node, env)
            return result

        if isinstance(node, Import):
            _handle_import(node, env)
            return None

        raise Exception(f"Unknown statement type: {type(node)} at {getattr(node, 'filename', None)}:{getattr(node,'lineno',None)}")
    except Exception as e:
        # augment error with node source if present
        raise

def _handle_import(node, env):
    # node.path is relative path (string) - resolve relative to node.filename or cwd
    base = os.path.dirname(node.filename) if node.filename and os.path.isabs(node.filename) or node.filename != "<input>" else os.getcwd()
    # if node.filename is like "<input>" (REPL), use cwd
    if node.filename and node.filename not in ("<input>", "<stdin>") and not os.path.isabs(node.filename):
        # if relative path provided, base relative to current working dir
        base = os.path.dirname(os.path.abspath(node.filename))
    target = node.path
    # if target is relative, join with base
    target_path = os.path.normpath(os.path.join(base, target))
    abs_path = os.path.abspath(target_path)
    if abs_path in _loaded_modules:
        module_env = _loaded_modules[abs_path]
        # import all top-level symbols into current env
        for k, v in module_env.vars.items():
            env.declare(k, v)
        return
    if abs_path in _loading:
        raise Exception(f"Circular import detected for {abs_path} at {node.filename}:{node.lineno}")
    if not os.path.exists(abs_path):
        raise Exception(f"Module file not found: {abs_path} at {node.filename}:{node.lineno}")
    _loading.add(abs_path)
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            code = f.read()
        from lexer import tokenize
        from parser import Parser
        toks = tokenize(code, filename=abs_path)
        parser = Parser(toks)
        stmts = parser.parse()
        module_env = Environment(parent=None)
        # interpret module statements in their own env
        interpret(stmts, module_env)
        # cache
        _loaded_modules[abs_path] = module_env
        # import symbols into current env
        for k, v in module_env.vars.items():
            env.declare(k, v)
    finally:
        _loading.discard(abs_path)

def _call_function_node(call_node, env):
    # evaluate callee then call as function
    callee_val = evaluate(call_node.callee, env)
    if not isinstance(callee_val, FunctionValue):
        raise Exception(f"Attempt to call non-function value at {call_node.filename}:{call_node.lineno}")
    # evaluate args
    arg_vals = [evaluate(a, env) for a in call_node.args]
    # prepare call env with closure_env as parent
    call_env = Environment(parent=callee_val.closure_env)
    # bind params
    for i, pname in enumerate(callee_val.params):
        pval = arg_vals[i] if i < len(arg_vals) else None
        call_env.declare(pname, pval)
    # push call frame
    _call_stack.append((callee_val.name or "<anonymous>", callee_val.def_filename, callee_val.def_lineno))
    try:
        for s in callee_val.body:
            execute(s, call_env)
    except ReturnException as re:
        _call_stack.pop()
        return re.value
    except Exception as e:
        # on exception, include call stack context and re-raise
        _call_stack.pop()
        raise
    _call_stack.pop()
    return None

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
    try:
        if isinstance(node, Number):
            return node.value
        if isinstance(node, String):
            return node.value
        if isinstance(node, Boolean):
            return node.value
        if isinstance(node, Var):
            try:
                return env.get(node.name)
            except Exception as e:
                raise Exception(f"{e} at {node.filename}:{node.lineno}")
        if isinstance(node, UnaryOp):
            val = evaluate(node.operand, env)
            if node.op == '!':
                return not truthy(val)
            if node.op == '-':
                if isinstance(val, (int, float)):
                    return -val
                raise Exception(f"Unary '-' applied to non-number at {node.filename}:{node.lineno}")
            raise Exception(f"Unknown unary operator: {node.op} at {node.filename}:{node.lineno}")
        if isinstance(node, BinOp):
            op = node.op
            # logical OR short-circuit
            if op == '||':
                left = evaluate(node.left, env)
                if truthy(left):
                    return True
                right = evaluate(node.right, env)
                return truthy(right)
            if op == '&&':
                left = evaluate(node.left, env)
                if not truthy(left):
                    return False
                right = evaluate(node.right, env)
                return truthy(right)
            left = evaluate(node.left, env)
            right = evaluate(node.right, env)
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
            if op == '<': return left < right
            if op == '>': return left > right
            if op == '<=': return left <= right
            if op == '>=': return left >= right
            if op == '==': return left == right
            if op == '!=': return left != right
            raise Exception(f"Unknown binary operator: {op} at {node.filename}:{node.lineno}")
        if isinstance(node, Call):
            return _call_function_node(node, env)
        raise Exception(f"Cannot evaluate node of type: {type(node)} at {getattr(node,'filename',None)}:{getattr(node,'lineno',None)}")
    except Exception as e:
        # propagate exception (already augmented where useful)
        raise
