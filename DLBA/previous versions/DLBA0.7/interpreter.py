# interpreter.py - DLBA interpreter (v0.7)
import os

from ast_nodes import *
from env import Environment
from lexer import SOURCE_MAP

# module cache & loading guard
_loaded_modules = {}  # abs_path -> module_env
_loading = set()

# call stack for runtime traces
_call_stack = []


def get_call_stack():
    return list(_call_stack)


class ReturnException(Exception):
    def __init__(self, value):
        super().__init__("Function returned")
        self.value = value


class FunctionValue:
    def __init__(
        self, params, body, closure_env, name=None, def_filename=None, def_lineno=None
    ):
        self.params = params
        self.body = body
        self.closure_env = closure_env
        self.name = name
        self.def_filename = def_filename
        self.def_lineno = def_lineno


class NativeFunction:
    def __init__(self, pyfunc, name=None):
        self.pyfunc = pyfunc
        self.name = name or getattr(pyfunc, "__name__", "<native>")

    def call(self, args):
        return self.pyfunc(*args)


class ModuleValue:
    def __init__(self, module_env, name=None, path=None):
        self.module_env = module_env
        self.name = name
        self.path = path

    def get_member(self, name):
        return self.module_env.get(name)


def interpret(statements, env, current_filename=None):
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
                raise Exception(
                    f"Undefined variable '{node.name}'. Use 'let' to declare it first. at {node.filename}:{node.lineno}"
                )
        return None

    if isinstance(node, FunctionDef):
        fv = FunctionValue(
            node.params,
            node.body,
            env,
            name=node.name,
            def_filename=node.filename,
            def_lineno=node.lineno,
        )
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
        for econd, ebranch in node.elif_branches:
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

    if isinstance(node, Import):
        _handle_import(node, env)
        return None

    # expression statement (like call)
    if isinstance(
        node,
        (
            Call,
            Var,
            ModuleAccess,
            Index,
            ListLiteral,
            DictLiteral,
            BinOp,
            UnaryOp,
            Number,
            String,
            Boolean,
        ),
    ):
        _ = evaluate(node, env)
        return None

    raise Exception(
        f"Unknown statement type: {type(node)} at {getattr(node,'filename',None)}:{getattr(node,'lineno',None)}"
    )


def _resolve_module_path(import_node):
    # resolve relative to import_node.filename if available, else cwd
    base = os.getcwd()
    if (
        import_node.filename
        and import_node.filename not in ("<input>", "<stdin>")
        and not os.path.isabs(import_node.filename)
    ):
        base = os.path.dirname(os.path.abspath(import_node.filename))
    target = import_node.path
    # try relative path as given; if it's not absolute, join with base
    candidate = os.path.normpath(os.path.join(base, target))
    if os.path.exists(candidate):
        return os.path.abspath(candidate)
    # also try current working dir
    candidate2 = os.path.normpath(os.path.join(os.getcwd(), target))
    if os.path.exists(candidate2):
        return os.path.abspath(candidate2)
    # try modules/ subdir
    candidate3 = os.path.normpath(os.path.join(os.getcwd(), "modules", target))
    if os.path.exists(candidate3):
        return os.path.abspath(candidate3)
    return os.path.abspath(candidate)  # fallback


def _handle_import(node, env):
    abs_path = _resolve_module_path(node)
    if abs_path in _loaded_modules:
        module_env = _loaded_modules[abs_path]
    else:
        if abs_path in _loading:
            raise Exception(
                f"Circular import detected for {abs_path} at {node.filename}:{node.lineno}"
            )
        if not os.path.exists(abs_path):
            raise Exception(
                f"Module file not found: {abs_path} at {node.filename}:{node.lineno}"
            )
        _loading.add(abs_path)
        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                code = f.read()
            from parser import Parser

            from lexer import tokenize

            toks = tokenize(code, filename=abs_path)
            parser = Parser(toks)
            stmts = parser.parse()
            module_env = Environment(parent=None)
            # register stdlib into module env as well for convenience
            register_stdlib(module_env)
            interpret(stmts, module_env)
            _loaded_modules[abs_path] = module_env
        finally:
            _loading.discard(abs_path)
    # import behavior
    if node.names:
        # from "path" import a, b -> bind only those names into env
        for name in node.names:
            try:
                val = module_env.get(name)
            except Exception:
                raise Exception(
                    f"Module {abs_path} has no name '{name}' at {node.filename}:{node.lineno}"
                )
            env.declare(name, val)
    elif node.as_name:
        # bind module object to name
        modval = ModuleValue(module_env, name=node.as_name, path=abs_path)
        env.declare(node.as_name, modval)
    else:
        # legacy behavior: import top-level symbols into current env
        for k, v in module_env.vars.items():
            env.declare(k, v)


def _call_function_value(fv, arg_vals):
    call_env = Environment(parent=fv.closure_env)
    for i, pname in enumerate(fv.params):
        pval = arg_vals[i] if i < len(arg_vals) else None
        call_env.declare(pname, pval)
    _call_stack.append((fv.name or "<anonymous>", fv.def_filename, fv.def_lineno))
    try:
        for s in fv.body:
            execute(s, call_env)
    except ReturnException as re:
        _call_stack.pop()
        return re.value
    except Exception:
        _call_stack.pop()
        raise
    _call_stack.pop()
    return None


def evaluate(node, env):
    if isinstance(node, Number):
        return node.value
    if isinstance(node, String):
        return node.value
    if isinstance(node, Boolean):
        return node.value
    if isinstance(node, Var):
        try:
            v = env.get(node.name)
            return v
        except Exception:
            # include file:line:col if available
            col = getattr(node, "col", None)
            if col:
                raise Exception(
                    f"Undefined variable '{node.name}' at {node.filename}:{node.lineno}:{col}"
                )
            else:
                raise Exception(
                    f"Undefined variable '{node.name}' at {node.filename}:{node.lineno}"
                )

    if isinstance(node, UnaryOp):
        try:
            val = evaluate(node.operand, env)
        except Exception as e:
            raise Exception(f"{e} at {node.filename}:{node.lineno}")
        if node.op == "!":
            return not truthy(val)
        if node.op == "-":
            if isinstance(val, (int, float)):
                return -val
            raise Exception(
                f"Unary '-' applied to non-number at {node.filename}:{node.lineno}"
            )
        raise Exception(
            f"Unknown unary operator: {node.op} at {node.filename}:{node.lineno}"
        )
    if isinstance(node, BinOp):
        op = node.op
        if op == "||":
            left = evaluate(node.left, env)
            if truthy(left):
                return True
            right = evaluate(node.right, env)
            return truthy(right)
        if op == "&&":
            left = evaluate(node.left, env)
            if not truthy(left):
                return False
            right = evaluate(node.right, env)
            return truthy(right)
        left = evaluate(node.left, env)
        right = evaluate(node.right, env)
        if op == "+":
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            return left / right
        if op == "%":
            return left % right
        if op == "<":
            return left < right
        if op == ">":
            return left > right
        if op == "<=":
            return left <= right
        if op == ">=":
            return left >= right
        if op == "==":
            return left == right
        if op == "!=":
            return left != right
        raise Exception(
            f"Unknown binary operator: {op} at {node.filename}:{node.lineno}"
        )
    if isinstance(node, Call):
        callee_val = evaluate(node.callee, env)
        arg_vals = [evaluate(a, env) for a in node.args]
        # FunctionValue
        if isinstance(callee_val, FunctionValue):
            return _call_function_value(callee_val, arg_vals)
        # NativeFunction
        if isinstance(callee_val, NativeFunction):
            try:
                return callee_val.call(arg_vals)
            except Exception as e:
                raise Exception(
                    f"Error in native function {callee_val.name}: {e} at {node.filename}:{node.lineno}"
                )
        raise Exception(
            f"Attempt to call a non-function value at {node.filename}:{node.lineno}"
        )
    if isinstance(node, ModuleAccess):
        obj = evaluate(node.obj, env)
        if isinstance(obj, ModuleValue):
            try:
                return obj.get_member(node.member)
            except Exception:
                raise Exception(
                    f"Module has no member '{node.member}' at {node.filename}:{node.lineno}"
                )
        if isinstance(obj, dict):
            return obj.get(node.member, None)
        raise Exception(
            f"Cannot access member '{node.member}' of non-module at {node.filename}:{node.lineno}"
        )
    if isinstance(node, ListLiteral):
        return [evaluate(e, env) for e in node.elements]
    if isinstance(node, DictLiteral):
        d = {}
        for k_node, v_node in node.pairs:
            key = evaluate(k_node, env)
            if not isinstance(key, str):
                key = str(key)
            d[key] = evaluate(v_node, env)
        return d
    if isinstance(node, Index):
        target = evaluate(node.target, env)
        idx = evaluate(node.index_expr, env)
        if isinstance(target, list):
            if not isinstance(idx, int):
                raise Exception(
                    f"List index must be integer at {node.filename}:{node.lineno}"
                )
            try:
                return target[idx]
            except IndexError:
                raise Exception(
                    f"List index out of range at {node.filename}:{node.lineno}"
                )
        if isinstance(target, dict):
            return target.get(idx, None)
        raise Exception(
            f"Indexing not supported on this value at {node.filename}:{node.lineno}"
        )
    raise Exception(
        f"Cannot evaluate node of type: {type(node)} at {getattr(node,'filename',None)}:{getattr(node,'lineno',None)}"
    )


def truthy(value):
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return len(value) != 0
    if isinstance(value, (list, dict)):
        return len(value) != 0
    return True


# -------------------------
# Standard library support
# -------------------------
def register_stdlib(env):
    # only register once per environment
    # define simple native functions mapping DLBA arguments to Python
    def _len(x):
        try:
            return len(x)
        except Exception:
            raise Exception("len() argument must be a collection or string")

    def _str(x=None):
        return "" if x is None else str(x)

    def _int(x):
        return int(x)

    def _float(x):
        return float(x)

    def _abs(x):
        return abs(x)

    def _min(*args):
        return min(*args)

    def _max(*args):
        return max(*args)

    def _read_file(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _write_file(path, content):
        with open(path, "w", encoding="utf-8") as f:
            f.write(str(content))
            return None

    def _range(a, b=None):
        if b is None:
            return list(range(a))
        return list(range(a, b))

    # register
    natives = {
        "len": NativeFunction(_len, "len"),
        "str": NativeFunction(_str, "str"),
        "int": NativeFunction(_int, "int"),
        "float": NativeFunction(_float, "float"),
        "abs": NativeFunction(_abs, "abs"),
        "min": NativeFunction(_min, "min"),
        "max": NativeFunction(_max, "max"),
        "read_file": NativeFunction(_read_file, "read_file"),
        "write_file": NativeFunction(_write_file, "write_file"),
        "range": NativeFunction(_range, "range"),
    }
    # add dlba module info
    dlba_mod = {
        "argv": [],
    }
    # declare natives and dlba module into env
    for k, v in natives.items():
        env.declare(k, v)
    env.declare("dlba", dlba_mod)


# -------------------------
# Traceback formatting
# -------------------------
def format_traceback(exc):
    print("---- DLBA Runtime Error ----")
    # call stack
    try:
        cs = get_call_stack()
        if cs:
            print("Call stack (most recent call last):")
            for name, filename, lineno in reversed(cs):
                print(f"  in {name} at {filename}:{lineno}")
    except Exception:
        pass
    # exception text
    print("Error:", exc)
    # try to show source line and caret if location info found in exception text
    # attempt to parse filename:lineno from exception message
    msg = str(exc)
    # Look for pattern ' at filename:lineno' at end
    import re

    m = re.search(r"at ([^:]+):([0-9]+)(?::([0-9]+))?", msg)
    if m:
        fname = m.group(1)
        lineno = int(m.group(2))
        col = int(m.group(3)) if m.group(3) else None
        lines = SOURCE_MAP.get(fname)
        if lines and 1 <= lineno <= len(lines):
            src = lines[lineno - 1]
            print(f'  File "{fname}", line {lineno}')
            print("    " + src)
            if col:
                # replace tabs with spaces to align caret (approximate)
                prefix = src[: max(0, col - 1)].replace("\t", "    ")
                caret_pos = len(prefix)
                print("    " + " " * caret_pos + "^")
