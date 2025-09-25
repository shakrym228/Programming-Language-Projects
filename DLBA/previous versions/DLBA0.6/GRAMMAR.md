# DLBA v0.6 — Language Grammar & Syntax

This document describes the concrete syntax and an EBNF-like grammar for **DLBA version 0.6**. It is written to match the current interpreter implementation (lexer → parser → AST → interpreter) and reflects the latest features: namespaced imports, module member access (dot), lists & dictionaries, statement-terminator rules, and canonical boolean literals (`True`/`False`).

---

## Lexical overview (tokens)

* **Keywords:** `import`, `as`, `func`, `return`, `let`, `if`, `elif`, `else`, `while`, `print`
* **Boolean literals:** `True`, `False` (capitalized)
* **Identifiers:** `[A-Za-z_][A-Za-z0-9_]*`
* **Numbers:** integers (`42`) and floats (`3.14`). Note: lexer emits both as `NUMBER` (with Python `int` or `float` value).
* **Strings:** double-quoted: `"hello \"world\""` (escape sequences supported)
* **Operators / punctuation:** `+ - * / % == != < > <= >= && || ! = ; , : ( ) { } [ ] .`
* **Comments:**

  * Single-line: `// this is a comment` (goes to end of line)
  * Multi-line: `/* comment \n can span lines */` (newlines inside preserved so line numbers remain consistent)
* **Separators:** NEWLINE tokens are significant and act as statement separators (see statement rules).

---

## High-level syntax rules (summary)

* Files use `.dlba` extension.
* Statements must be separated by one of: semicolon `;`, a newline, or by the end of a block `}`. Examples accepted:

  * `print 0; print 1`
  * `print 0\nprint 1` (newline between statements)
  * A trailing semicolon is allowed: `print 0;` followed by newline.
  * **Invalid**: `print 0 print 1` — missing separator.
* Boolean literals are strict: only `True` and `False` are recognized as booleans (lowercase `true`/`false` are treated as identifiers).
* `import "path"` (legacy) imports top-level names into current environment; `import "path" as alias` binds a module object to `alias` (use `alias.member` to access).

---

## Concrete examples

```dlba
// variable declaration and reassignment
let x = 10
x = x + 1

// function declaration and call
func add(a, b) {
    return a + b
}
print(add(2, 3))

// namespaced import
import "utils.dlba" as utils
print(utils.MODULE_NAME)
print(utils.inc(5))

// list and dict literals and indexing
let arr = [1, 2, 3]
print(arr[0])
let map = {"a": 1, b: 2}
print(map["b"])

// separators: both forms valid
print 0; print 1
print 2
print 3
```

---

## EBNF-like grammar (recommended to match parser)

```
program        := statement*

# Statements (must be followed by ';' or NEWLINE or RBRACE/EOF)
statement      := var_decl
                | assignment
                | print_stmt
                | if_stmt
                | while_stmt
                | func_decl
                | return_stmt
                | import_stmt
                | expr_stmt

var_decl       := "let" IDENT "=" expr
assignment     := IDENT "=" expr
print_stmt     := "print" ("(" expr ")" | expr)

import_stmt    := "import" STRING [ "as" IDENT ]

func_decl      := "func" IDENT "(" [ param_list ] ")" block
param_list     := IDENT { "," IDENT }
return_stmt    := "return" [ expr ]

if_stmt        := "if" "(" expr ")" block
                { "elif" "(" expr ")" block }
                [ "else" block ]

while_stmt     := "while" "(" expr ")" block

block          := "{" statement* "}"

expr_stmt      := expr

# Expressions with precedence (postfix supports call, dot, indexing)
expr           := or_expr
or_expr        := and_expr { ("||" | "or") and_expr }
and_expr       := equality { ("&&" | "and") equality }
equality       := comparison { ("==" | "!=") comparison }
comparison     := additive { ("<" | ">" | "<=" | ">=") additive }
additive       := term { ("+" | "-") term }
term           := factor { ("*" | "/" | "%") factor }
factor         := ("!" | "not" | "-") factor | postfix
postfix        := primary { call | member | index }
call           := "(" [ arg_list ] ")"
member         := "." IDENT
index          := "[" expr "]"
arg_list       := expr { "," expr }
primary        := NUMBER | FLOAT | STRING | TRUE | FALSE | IDENT | "(" expr ")" | list_literal | dict_literal
list_literal   := "[" [ expr { "," expr } ] "]"
dict_literal   := "{" [ (STRING | IDENT) ":" expr { "," (STRING | IDENT) ":" expr } ] "}"

# Terminator rule (parser enforces): after any top-level statement or a statement inside a block,
# the next token must be one of SEMICOLON, NEWLINE, RBRACE, or EOF. Otherwise a parse error is raised.
```

---

## Notes about implementation details (mapping to code)

* **Lexer**: emits tokens including `NEWLINE` (significant), token objects contain `(type, value, lineno, col, filename)` used by parser and interpreter for diagnostics.
* **Parser**: centralizes terminator handling — it consumes `NEWLINE` or `SEMICOLON` after each statement (or allows `RBRACE` / EOF). It also implements postfix expression parsing (call, dot, index) and parses list/dict literals.
* **AST nodes**: include `FunctionDef`, `Call`, `ModuleAccess` (dot), `ListLiteral`, `DictLiteral`, `Index`, `Import` (with `as_name`). Nodes carry `lineno` and `filename` for error reporting.
* **Interpreter**:

  * `import "path" as alias` loads the module file and binds a `ModuleValue` under `alias`; `ModuleValue.get_member(name)` returns the module's top-level binding.
  * `import "path"` without `as` imports top-level names directly into the current environment (legacy behavior preserved).
  * Lists evaluate to Python lists, dicts to Python dicts, indexing supports integer indices for lists and key lookup for dicts.
  * Boolean literals evaluate to Python `True`/`False`.

---

## Error and diagnostic guidelines

* Parser errors include `filename:lineno` and a short message (e.g. `Expected ';' or newline after statement but got IDENT at file.dlba:12`).
* Runtime errors attempt to include call-stack frames (function name, definition filename and lineno) as produced by the interpreter's `_call_stack` when available.

---