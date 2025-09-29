# DLBA v0.8 — Grammar & Language Reference

This document is the formal reference for **DLBA version 0.8**. It describes lexical tokens, syntax, operator precedence, standard library conventions, module/package resolution, and runtime semantics relevant to the implementation in this repository.

---

## 1. Lexical tokens

* **Keywords:** `import`, `from`, `as`, `func`, `return`, `let`, `if`, `elif`, `else`, `while`, `print`
* **Boolean literals:** `True`, `False` (lexer also accepts `true`/`false` and normalizes them)
* **Identifiers:** `[A-Za-z_][A-Za-z0-9_]*`
* **Numbers:** integers (`42`) and floats (`3.14`) — tokens emitted as `NUMBER` with Python `int`/`float` value
* **Strings:** double-quoted with escapes: `"..."`
* **Operators & punctuation:** `+ - * / % == != < > <= >= && || ! = ; , : ( ) { } [ ] .`
* **Comments:**

  * Single-line: `// comment` (till end-of-line)
  * Multi-line: `/* comment */` (preserves newlines so reported line numbers remain accurate)
* **Whitespace/newlines:** NEWLINE tokens are significant as statement separators. Tabs/spaces are SKIP tokens.

---

## 2. Statement termination rules

A statement must be terminated by at least one of:

* a semicolon `;`, or
* a newline (NEWLINE token), or
* a closing brace `}` (end of block implicitly terminates the last statement).

Invalid: sequences of statements with no separator (e.g. `print 0 print 1`) will produce a parse error.

---

## 3. High-level syntax (EBNF-like)

```
program        := statement*

statement      := var_decl
               | assignment
               | print_stmt
               | import_stmt
               | func_decl
               | return_stmt
               | if_stmt
               | while_stmt
               | expr_stmt

var_decl       := "let" IDENT "=" expr
assignment     := IDENT "=" expr
print_stmt     := "print" ("(" expr ")" | expr)

import_stmt    := "import" STRING ["as" IDENT]
               | "from" STRING "import" IDENT {"," IDENT}

func_decl      := "func" IDENT "(" [param_list] ")" block
param_list     := IDENT {"," IDENT}
return_stmt    := "return" [expr]

if_stmt        := "if" "(" expr ")" block { "elif" "(" expr ")" block } [ "else" block ]
while_stmt     := "while" "(" expr ")" block
block          := "{" statement* "}"

expr_stmt      := expr

expr           := or_expr
or_expr        := and_expr { ("||" | "or") and_expr }
and_expr       := equality { ("&&" | "and") equality }
equality       := comparison { ("==" | "!=") comparison }
comparison     := additive { ("<" | ">" | "<=" | ">=") additive }
additive       := term { ("+" | "-") term }
term           := factor { ("*" | "/" | "%") factor }
factor         := ("!" | "not" | "-") factor | postfix
postfix        := primary { call | member | index }
call           := "(" [arg_list] ")"
member         := "." IDENT
index          := "[" ( slice | expr ) "]"
slice          := [expr] ":" [expr]
arg_list       := expr {"," expr}
primary        := NUMBER | STRING | TRUE | FALSE | IDENT | "(" expr ")" | list_literal | dict_literal
list_literal   := "[" [ expr {"," expr } ] "]"
dict_literal   := "{" [ (STRING | IDENT) ":" expr {"," (STRING | IDENT) ":" expr } ] "}"
```

Notes:

* `member` followed by `call` supports instance method syntax like `arr.append(1)` (represented as `Call(ModuleAccess(...), args)`).
* `index` supports slices `a[1:3]` and single indices `a[2]`.

---

## 4. Operator precedence (highest → lowest)

1. Postfix: function call `()`, member access `.`, indexing `[]`
2. Unary: `!`, `not`, `-` (right-to-left)
3. Multiplicative: `*`, `/`, `%` (left-to-right)
4. Additive: `+`, `-` (left-to-right)
5. Comparison: `<`, `>`, `<=`, `>=` (left-to-right)
6. Equality: `==`, `!=`
7. Logical AND: `&&` / `and`
8. Logical OR: `||` / `or`

String concatenation uses `+` and coerces non-strings via `str()` conversion in the interpreter.

---

## 5. Types & runtime values

* **Primitive:** `int`, `float`, `str`, `bool`
* **Collection:** `list` (Python list), `dict` (string keys by default)
* **Function:** user-defined `FunctionValue` (callable), `NativeFunction` (builtin wrappers), `NativeMethod` (method wrappers bound to an instance)
* **Module:** `ModuleValue` (module namespace)
* **File:** `FileValue` wrapping a Python file object with `.read()`, `.write()`, `.close()` methods

Type coercion rules (interpreter-level):

* `+` between strings and non-strings: non-strings converted with `str()` and concatenated.
* Arithmetic ops operate on numbers; type errors produce runtime exceptions with source location.

---

## 6. Collections & methods

* Lists support literal creation `[1,2,3]` and methods via member-call wrappers: `append`, `pop`, `insert`, `index`, `count`, and slicing `a[start:stop]`.
* Dict literals use string keys or identifier keys (identifier keys are converted to strings): `{ "a":1, b:2 }`. Dict methods: `keys()`, `values()`, `items()`, `get(key)`, `pop(key)`.
* Strings expose `format(...)`, `upper()`, `lower()` via method syntax.

Example:

```dlba
let a = [1,2]
a.append(3)
print(a[1:3])   // [2,3]
let d = {x: 10, "y": 20}
print(d.keys())
print("Hi {}".format("You"))
```

---

## 7. Modules & packages

**Import forms**

* `import "path/to/module.dlba"` — legacy: import top-level names into current environment.
* `import "path/to/module.dlba" as mod` — bind a module object to `mod`.
* `from "path/to/module.dlba" import name1, name2` — import only specific names.

**Package support**

* If `path` resolves to a directory containing `__init__.dlba`, interpreter loads that `__init__.dlba` as the module. Subpackages are supported by specifying path segments.

**Resolution order** (attempted by the interpreter):

1. Directory of importing file (if applicable) — e.g. importer `dir/importer.dlba` will search `dir/target`.
2. Current working directory.
3. `modules/` subdirectory in project root.
4. Fallback: normalized absolute path of the provided `path`.

**Module caching & circular imports**

* Modules are cached after first load (`_loaded_modules`). Circular import detection prevents infinite recursion and raises a clear error including file/line.

---

## 8. Standard library (selected functions)

Available by default in each new `Environment` via `register_stdlib`:

* `len(x)` — length of collection or string
* `str(x)` — convert to string
* `int(x)`, `float(x)` — numeric conversion
* `abs(x)`, `min(..)`, `max(..)`
* `read_file(path)`, `write_file(path, content)`
* `open(path, mode)` — returns `FileValue` with `.read()`, `.write()`, `.close()`.
* `range(n)` / `range(a,b)` — returns list of ints
* `dlba` module container with `argv` list

Note: list/dict/string instance methods are provided via `NativeMethod` wrappers (retrieved on `ModuleAccess` evaluation for instances).

---

## 9. Error reporting

* Parse and runtime errors include `filename:line:column` where possible. The interpreter prints the source line and a caret (`^`) under the error column.
* Runtime errors also include an optional call stack showing function names and definition locations.
* Example error:

```
---- DLBA Runtime Error ----
Error: Undefined variable 'v' at main_test_v0_8_full.dlba:11:7
  File "main_test_v0_8_full.dlba", line 11
    print(v)
         ^
```

---

## 10. Packaging & distribution notes (pre-v1.0)

To create a standalone executable of a DLBA program for distribution, two practical approaches exist:

1. **Bundle interpreter + script** — use tools such as PyInstaller to pack the Python interpreter and project files into a single executable. Fast and simple; exe size will include Python runtime.
2. **Bytecode + small VM** — compile DLBA AST to a bytecode file and ship a small VM runtime that executes it. Produces smaller executables but requires designing a bytecode format and VM.

Recommended path to v1.0: implement bytecode+VM in v0.9 and provide a bundling tool (PyInstaller wrapper) as a convenience for end users.

---

## 11. Examples

See `main_test_v0_8_full.dlba` for a comprehensive set of examples covering modules, IO, slicing, methods, and package imports.

---