# DLBA — Version 0.7

**Release:** 0.7 — **2025-09-25**
**Author:** Mahdi Shakeri

---

## Overview

DLBA (Design Language By Example) is a small, educational scripting language implemented in Python. Version **0.7** focuses on developer ergonomics and practical tooling: a small standard library, improved error tracebacks (with file\:line\:column and caret), polished REPL (history & multiline), more robust import resolution, and `from "file" import name` support.

This README reflects the current codebase (files and behaviors) and is intended for contributors and users who want to run or extend DLBA locally.

---

## Highlights / What’s new in 0.7

* **Standard library (stdlib):** built-in functions such as `len`, `str`, `int`, `float`, `range`, `read_file`, `write_file`, etc. (registered into every Environment).
* **Improved tracebacks:** runtime and parse errors now include `filename:line:column` and display the source line plus a caret indicating the error column when available.
* **REPL improvements:** history (via `readline` when available), persistent history file, and multiline input support.
* **Import enhancements:** better resolution (relative to importing file, working directory, and `modules/`), module caching, circular import detection, and `from "path" import name` syntax.
* **Native functions:** `NativeFunction` wrapper to expose Python-implemented builtins while keeping interpreter call semantics.
* **Compatibility:** lowercase `true` / `false` are accepted and normalized for backwards compatibility (but canonical booleans are `True` / `False`).

---

## Project layout (major files)

* `main.py` — CLI entry point (runs a `.dlba` file or starts the REPL).
* `repl.py` — interactive REPL with history and multiline input.
* `lexer.py` — tokenizer (produces tokens with `lineno`, `col`, `filename`) and maintains `SOURCE_MAP` for source display.
* `parser.py` — recursive-descent parser (supports postfix calls, dot access, list/dict literals, `from`/`import`/`as`).
* `ast_nodes.py` — AST node classes.
* `interpreter.py` — evaluator and runtime (module loader, native functions, call stack, traceback formatting).
* `env.py` — environment / scopes (declare, set, get, exists, parent chain).
* `stdlib.py` — light wrapper / loader (calls `interpreter.register_stdlib`).
* `utils.dlba`, `math_extra.dlba` — example modules used by tests.
* `main_test_v0_7_full.dlba` — comprehensive test script covering language features.

---

## Language summary (quick)

* File extension: `.dlba`
* Statement separators: `;` or newline (or end-of-block `}`)
* Declarations: `let name = expr`; reassignment uses `name = expr` (without `let`)
* Functions: `func name(params) { ... }` and `return`
* Imports: `import "file.dlba" [as alias]` and `from "file.dlba" import name1, name2`
* Collections: lists `[1,2,3]`, dictionaries `{"k": v, id: v}` (IDENT keys are converted to string keys)
* Booleans: `True`, `False` (lowercase `true`/`false` accepted and normalized)
* Operators: `+ - * / %`, comparisons `== != < > <= >=`, logical `&& || !` (and `and`/`or`/`not` synonyms)
* Strings: double-quoted with typical escapes `"\n"`

---

## Installation (local)

1. Clone the repository:

```bash
git clone https://github.com/<your-username>/DLBA.git
cd DLBA/DLBA0.7
```

2. Run DLBA on a file:

```bash
python main.py main_test_v0_7_full.dlba
```

3. Or start the REPL:

```bash
python main.py
```

> Requirements: Python 3.8+ (for typing and str/unicode handling). `readline` improves REPL but is optional.

---

## Usage examples

Run the provided comprehensive test:

```bash
python main.py main_test_v0_7_full.dlba
```

Expected behaviors include: module imports (`import "utils.dlba" as utils`), `from`-imports, function calls, recursion, lists & dicts indexing, stdlib functions (`len`, `str`, `int`, `float`, `range`), file I/O (`read_file` / `write_file`), and proper tracebacks on errors.

---

## Error reporting and debugging

When a parse or runtime error occurs the interpreter prints a friendly diagnostic block containing:

* a one-line error summary,
* an optional call stack (most recent call last),
* the source line containing the error and a caret showing the column (if available).

Example:

```
---- DLBA Runtime Error ----
Error: Undefined variable 'v' at main_test_v0_7_full.dlba:11:7
  File "main_test_v0_7_full.dlba", line 11
      print("len test: " + len([1,2,3]))
           ^
```

If you see line/column mismatches, ensure your test files are saved with UTF-8 and that you are running the very copy of the file you edited (the interpreter uses `SOURCE_MAP[filename]` to retrieve source lines).

---

## Development notes

* **Where to add builtins:** implement a new Python function in `interpreter.register_stdlib` and wrap it with `NativeFunction`.
* **Adding AST nodes:** add the class in `ast_nodes.py`, update `parser.py` to emit the node and `interpreter.py` to evaluate it.
* **Module search:** `_resolve_module_path()` in `interpreter.py` looks in the importing file's directory, current working directory, and `modules/`.
* **Caching & packaging:** modules are cached in `_loaded_modules` to avoid re-execution and to detect circular imports.

---

## Testing

* Use `main_test_v0_7_full.dlba` for a full feature run.
* For unit testing, consider writing small Python test scripts that call `tokenize()`, `Parser(tokens).parse()`, and `interpret()` on controlled inputs and compare outputs.

---

## Roadmap (next steps: v0.8 → v1.0)

* **v0.8:** packages (`__init__`-style), richer collection APIs (slicing, list methods), more stdlib (I/O helpers bundled), and packaging support (modules folder conventions).
* **v0.9:** formatter, linter, test harness, optional AST/bytecode cache for speed.
* **v1.0:** API freeze, comprehensive docs and examples, and stable release.

---

## Contributing

Contributions are welcome. Please:

1. Fork the repo and create a feature branch.
2. Add tests for new behaviors under `tests/` (or add new `.dlba` scripts).
3. Open a PR with a clear description and before/after examples.

---