# DLBA — Version 0.8

**Release:** 0.8 — **2025-09-29**
**Author:** Mahdi Shakeri

---

## Overview

DLBA (Design Language By Example) is a small educational scripting language implemented in Python. Version **0.8** is a large, focused upgrade that brings package support, richer standard library I/O, method-style member calls, collection APIs, slicing, and improved module resolution — all aimed at making DLBA practical for small development tasks and preparing the project for bytecode and bundling in future releases.

This README documents the current codebase (files and behaviors) and gives quick instructions for running, testing, and extending DLBA locally.

---

## What's new in 0.8

* **Package support**: directory packages with `__init__.dlba` are recognized. `import "pkg"` will load `pkg/__init__.dlba`.
* **Improved module resolution**: resolution order is importer-directory → current working directory → `modules/` directory; clearer errors for module-not-found and circular imports.
* **I/O primitives**: `open(path, mode)` returns a file object with `.read()`, `.write()`, and `.close()`; `read_file` and `write_file` convenience functions included.
* **Collection instance methods**: `list.append`, `list.pop`, `list.insert`, `list.index`, `list.count`, `dict.keys`, `dict.values`, `dict.items`, `dict.get`, and string methods like `.format()`, `.upper()`, `.lower()` are available via method-call syntax (e.g. `arr.append(1)`).
* **Slicing**: `a[start:stop]` supported for lists and strings.
* **NativeMethod wrapper**: an internal wrapper allows instance methods to be exposed without new AST nodes.
* **FileValue wrapper**: safer file handling for `open()` results.
* **Backwards compatibility preserved**: features from v0.7 remain supported (booleans, functions, modules, tracebacks with file:line:col caret, REPL history, etc.).

---

## Project layout (major files)

* `main.py` — CLI entry point (runs a `.dlba` file or starts the REPL).
* `repl.py` — interactive REPL with history and multiline input.
* `lexer.py` — tokenizer (produces tokens with `lineno`, `col`, `filename`) and maintains `SOURCE_MAP` for source display.
* `parser.py` — recursive-descent parser (supports calls, member access, indexing, slicing, lists/dicts, packages).
* `ast_nodes.py` — AST node classes (includes `Slice`).
* `interpreter.py` — evaluator and runtime (module loader, native functions, FileValue, NativeMethod, call stack, traceback formatting).
* `env.py` — environment / lexical scopes (declare, set, get, exists, parent chain).
* `stdlib.py` — wrapper to register standard library functions into every `Environment`.
* `modules/` — optional place for packages and modules.
* `utils.dlba`, `math_extra.dlba` — example modules.
* `main_test_v0_8_full.dlba` — comprehensive test script for v0.8.

---

## Quick start

1. Clone or copy the project files to a local folder.
2. Run the comprehensive test script:

```bash
python main.py main_test_v0_8_full.dlba
```

3. Or start the REPL:

```bash
python main.py
```

> Requirements: Python 3.8+ (recommended). `readline` improves REPL experience but is optional.

---

## Language highlights (quick)

* File extension: `.dlba`
* Statement separators: `;` or newline (or `}` closes a block)
* Variable declaration: `let x = 10`; reassignment: `x = expr`
* Functions: `func name(params) { ... }` and `return`
* Modules and packages: `import "pkg" as p`, `from "pkg.sub" import name`
* Collections: lists `[1,2,3]`, dicts `{"k": v, id: v}`, slicing `a[1:3]`
* Member calls: `arr.append(4)`, `m.keys()`, `t.format("x")`
* I/O: `open(path, mode)`, `read_file(path)`, `write_file(path, content)`
* Standard builtins: `len`, `str`, `int`, `float`, `abs`, `min`, `max`, `range`, and file helpers.

---

## Examples

**List methods and slicing**

```dlba
let a = [1,2,3]
a.append(4)
print(a)          // [1,2,3,4]
print(a[1:3])     // [2,3]
print(a.pop())    // 4
```

**Dict methods and string format**

```dlba
let m = {x: 10, "y": 20}
print(m.keys())
print("hello {}".format("world"))
```

**File I/O**

```dlba
let f = open("tmp.txt", "w")
f.write("hello\n")
f.close()
print(read_file("tmp.txt"))
```

**Package import**

```
// layout: mypkg/__init__.dlba
import "mypkg" as pkg
print(pkg.SOME_VALUE)
```

---

## Error reporting

When a parse or runtime error occurs, DLBA prints a diagnostic block that includes:

* a one-line error message,
* optional call stack (most recent call last),
* the offending source line and a caret pointing at the error column (when available).

If you see mismatched line numbers, ensure the file is saved in UTF-8 and you are running the same file path shown in the error.

---

## Testing & development

* Use `main_test_v0_8_full.dlba` to validate core behaviors.
* Add unit tests by calling `tokenize()`, `Parser(tokens).parse()`, and `interpret()` on small inputs.
* For packages, place package folders under the project root or `modules/` and include `__init__.dlba`.

---

## Roadmap to v1.0.0

* **v0.9:** Bytecode emitter + VM runner, caching of compiled modules, CI unit tests, and richer standard library.
* **v1.0.0:** Stable language spec, official packaging/bundling tools to create standalone executables (recommended initial strategy: bundle interpreter + script with PyInstaller; medium-term: small VM + bytecode runner for smaller EXEs).

---

## Contributing

* Fork the repo, add tests for new behaviors, and open a PR.
* Follow the existing AST → Parser → Interpreter pattern when adding language features.
---