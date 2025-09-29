# interpreter.py - DLBA interpreter (v0.8)
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


class NativeMethod:
    """
    wrapper for instance methods: binds an instance and method name
    calling returns the effect on that instance
    """

    def __init__(self, instance_holder, method_name):
        self.instance_holder = (
            instance_holder  # direct python value (list/dict/str/FileValue)
        )
        self.method_name = method_name

    def call(self, args):
        inst = self.instance_holder
        # list methods
        if isinstance(inst, list):
            if self.method_name == "append":
                inst.append(args[0] if args else None)
                return None
            if self.method_name == "pop":
                return inst.pop() if args == [] else inst.pop(args[0])
            if self.method_name == "insert":
                inst.insert(args[0], args[1])
                return None
            if self.method_name == "index":
                return inst.index(args[0])
            if self.method_name == "count":
                return inst.count(args[0])
            if self.method_name == "slice":
                # args: start, stop
                start, stop = args
                return inst[start:stop]
        # dict methods
        if isinstance(inst, dict):
            if self.method_name == "keys":
                return list(inst.keys())
            if self.method_name == "values":
                return list(inst.values())
            if self.method_name == "items":
                return list(inst.items())
            if self.method_name == "get":
                return inst.get(args[0], None)
            if self.method_name == "pop":
                return inst.pop(args[0])
        # string methods
        if isinstance(inst, str):
            if self.method_name == "format":
                # call Python str.format
                return inst.format(*args)
            if self.method_name == "upper":
                return inst.upper()
            if self.method_name == "lower":
                return inst.lower()
        # FileValue methods (FileValue class defined below)
        if isinstance(inst, FileValue):
            if self.method_name == "read":
                return inst.read()
            if self.method_name == "write":
                return inst.write(args[0] if args else "")
            if self.method_name == "close":
                return inst.close()
        raise Exception(
            f"Unknown method {self.method_name} for instance type {type(inst)}"
        )


class ModuleValue:
    def __init__(self, module_env, name=None, path=None):
        self.module_env = module_env
        self.name = name
        self.path = path

    def get_member(self, name):
        return self.module_env.get(name)


# File wrapper
class FileValue:
    def __init__(self, pyfile):
        self._pyfile = pyfile

    def read(self):
        try:
            self._pyfile.seek(0)
        except Exception:
            pass
        return self._pyfile.read()

    def write(self, content):
        self._pyfile.write(str(content))
        self._pyfile.flush()
        return None

    def close(self):
        try:
            self._pyfile.close()
        except Exception:
            pass
        return None


# -------------------------
# Interpreter core
# -------------------------
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
                    f"Undefined variable '{node.name}' at {node.filename}:{node.lineno}:{getattr(node,'col',None)}"
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


# -------------------------
# Module / package resolver
# -------------------------
def _resolve_module_path(import_node):
    """
    Resolve import_node.path (string) to an absolute path.
    Support:
      - explicit file paths: "utils.dlba"
      - package name (directory): "mypkg" -> mypkg/__init__.dlba
      - relative to importer's filename
      - cwd
      - modules/ subdir
    """
    target = import_node.path
    # if user provided with extension or path segments, respect them:
    base_candidates = []
    # if importing from a file, prefer that directory
    if import_node.filename and import_node.filename not in ("<input>", "<stdin>"):
        importer_dir = os.path.dirname(os.path.abspath(import_node.filename))
        base_candidates.append(os.path.join(importer_dir, target))
        base_candidates.append(
            os.path.join(
                importer_dir, target + ("" if target.endswith(".dlba") else "")
            )
        )
    # cwd
    base_candidates.append(os.path.join(os.getcwd(), target))
    # modules dir
    base_candidates.append(os.path.join(os.getcwd(), "modules", target))
    # now check candidates:
    for cand in base_candidates:
        # exact file
        if os.path.isfile(cand):
            return os.path.abspath(cand)
        # with .dlba
        if os.path.isfile(cand + ".dlba"):
            return os.path.abspath(cand + ".dlba")
        # package dir with __init__.dlba
        if os.path.isdir(cand):
            initf = os.path.join(cand, "__init__.dlba")
            if os.path.isfile(initf):
                return os.path.abspath(initf)
            # maybe cand + '.dlba' as file
            if os.path.isfile(cand + ".dlba"):
                return os.path.abspath(cand + ".dlba")
    # fallback: treat target as relative file path
    fallback = os.path.normpath(os.path.join(os.getcwd(), target))
    return os.path.abspath(fallback)


def _handle_import(node, env):
    abs_path = _resolve_module_path(node)
    if abs_path in _loaded_modules:
        module_env = _loaded_modules[abs_path]
    else:
        if abs_path in _loading:
            raise Exception(
                f"Circular import detected for {abs_path} at {node.filename}:{node.lineno}:{getattr(node,'col',None)}"
            )
        if not os.path.exists(abs_path):
            raise Exception(
                f"Module file not found: {abs_path} at {node.filename}:{node.lineno}:{getattr(node,'col',None)}"
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
            # register stdlib for module env as well
            register_stdlib(module_env)
            interpret(stmts, module_env)
            _loaded_modules[abs_path] = module_env
        finally:
            _loading.discard(abs_path)
    # import behavior
    if node.names:
        for name in node.names:
            try:
                val = module_env.get(name)
            except Exception:
                raise Exception(
                    f"Module {abs_path} has no name '{name}' at {node.filename}:{node.lineno}:{getattr(node,'col',None)}"
                )
            env.declare(name, val)
    elif node.as_name:
        modval = ModuleValue(module_env, name=node.as_name, path=abs_path)
        env.declare(node.as_name, modval)
    else:
        for k, v in module_env.vars.items():
            env.declare(k, v)


# -------------------------
# Function calling / evaluation
# -------------------------
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
        val = evaluate(node.operand, env)
        if node.op == "!":
            return not truthy(val)
        if node.op == "-":
            if isinstance(val, (int, float)):
                return -val
            raise Exception(
                f"Unary '-' applied to non-number at {node.filename}:{node.lineno}:{getattr(node,'col',None)}"
            )
        raise Exception(
            f"Unknown unary operator: {node.op} at {node.filename}:{node.lineno}"
        )
    if isinstance(node, BinOp):
        op = node.op
        # short-circuit for logicals
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
        try:
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
        except Exception as e:
            raise Exception(
                f"Error during binary op '{op}': {e} at {node.filename}:{node.lineno}:{getattr(node,'col',None)}"
            )
        raise Exception(
            f"Unknown binary operator: {op} at {node.filename}:{node.lineno}:{getattr(node,'col',None)}"
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
                    f"Error in native function {callee_val.name}: {e} at {node.filename}:{node.lineno}:{getattr(node,'col',None)}"
                )
        # NativeMethod bound
        if isinstance(callee_val, NativeMethod):
            try:
                return callee_val.call(arg_vals)
            except Exception as e:
                raise Exception(
                    f"Error in native method {callee_val.method_name}: {e} at {node.filename}:{node.lineno}:{getattr(node,'col',None)}"
                )
        raise Exception(
            f"Attempt to call a non-function value at {node.filename}:{node.lineno}:{getattr(node,'col',None)}"
        )
    if isinstance(node, ModuleAccess):
        obj = evaluate(node.obj, env)
        # Module member access (module object)
        if isinstance(obj, ModuleValue):
            try:
                return obj.get_member(node.member)
            except Exception:
                raise Exception(
                    f"Module has no member '{node.member}' at {node.filename}:{node.lineno}:{getattr(node,'col',None)}"
                )
        # For python-level instances (list/dict/str/FileValue), return a NativeMethod wrapper
        if (
            isinstance(obj, list)
            or isinstance(obj, dict)
            or isinstance(obj, str)
            or isinstance(obj, FileValue)
        ):
            # return a callable native-method wrapper
            return NativeMethod(obj, node.member)
        # For dicts, allow obj['key'] via ModuleAccess too? Prefer Index usage
        # If object is a Python dict and member is present as key, return it
        if isinstance(obj, dict) and node.member in obj:
            return obj[node.member]
        raise Exception(
            f"Cannot access member '{node.member}' of non-module/non-object at {node.filename}:{node.lineno}:{getattr(node,'col',None)}"
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
        idx_expr = node.index_expr
        # slicing
        if isinstance(idx_expr, Slice):
            start = (
                evaluate(idx_expr.start, env) if idx_expr.start is not None else None
            )
            stop = evaluate(idx_expr.stop, env) if idx_expr.stop is not None else None
            if isinstance(target, list):
                return target[slice(start, stop)]
            if isinstance(target, str):
                return target[slice(start, stop)]
            raise Exception(
                f"Slicing not supported on this value at {node.filename}:{node.lineno}:{getattr(node,'col',None)}"
            )
        else:
            idx = evaluate(idx_expr, env)
            if isinstance(target, list):
                if not isinstance(idx, int):
                    raise Exception(
                        f"List index must be integer at {node.filename}:{node.lineno}:{getattr(node,'col',None)}"
                    )
                try:
                    return target[idx]
                except IndexError:
                    raise Exception(
                        f"List index out of range at {node.filename}:{node.lineno}:{getattr(node,'col',None)}"
                    )
            if isinstance(target, dict):
                return target.get(idx, None)
            if isinstance(target, str):
                if not isinstance(idx, int):
                    raise Exception(
                        f"String index must be integer at {node.filename}:{node.lineno}:{getattr(node,'col',None)}"
                    )
                try:
                    return target[idx]
                except Exception:
                    raise Exception(
                        f"String index error at {node.filename}:{node.lineno}:{getattr(node,'col',None)}"
                    )
            raise Exception(
                f"Indexing not supported on this value at {node.filename}:{node.lineno}:{getattr(node,'col',None)}"
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
# Standard library support (extended)
# -------------------------
def register_stdlib(env):
    # minimal native wrappers
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

    def _open(path, mode="r"):
        # return a FileValue wrapping Python file
        pyf = open(path, mode, encoding="utf-8")
        return FileValue(pyf)

    def _range(a, b=None):
        if b is None:
            return list(range(a))
        return list(range(a, b))

    # register as NativeFunction
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
        "open": NativeFunction(_open, "open"),
        "range": NativeFunction(_range, "range"),
    }
    # add dlba module info container
    dlba_mod = {
        "argv": [],
    }
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
    # attempt to find filename:lineno:col
    import re

    m = re.search(r"at ([^:]+):([0-9]+)(?::([0-9]+))?", str(exc))
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
                prefix = src[: max(0, col - 1)].replace("\t", "    ")
                caret_pos = len(prefix)
                print("    " + " " * caret_pos + "^")
