# DLBA v0.7 — Language Grammar & Syntax

This document describes the concrete syntax and an EBNF-like grammar for **DLBA version 0.7**. It matches the current implementation (lexer → parser → AST → interpreter) and reflects features added up to v0.7: modules and namespaced imports, `from "path" import name`, stdlib builtins, lists & dicts, statement separator rules, and canonical boolean literals (`True`/`False`), with backward compatibility for lowercase `true`/`false`.

---

## Lexical tokens

* **Keywords:** `import`, `from`, `as`, `func`, `return`, `let`, `if`, `elif`, `else`, `while`, `print`
* **Boolean literals:** `True`, `False` (lexer also accepts `true`/`false` and normalizes them)
* **Identifiers:** `[A-Za-z_][A-Za-z0-9_]*`
* **Numbers:** integers (`42`) and floats (`3.14`) — both emitted as `NUMBER` tokens with `int` or `float` value.
* **Strings:** double-quoted: `"hello \"DLBA\""` (escape sequences supported)
* **Operators & punctuation:** `+ - * / % == != < > <= >= && || ! = ; , : ( ) { } [ ] .`
* **Comments:**

  * Single-line: `// comment` (to end of line)
  * Multi-line: `/* comment\n can span lines */` (preserves newline count so line numbers remain accurate)
* **Whitespace/newlines:** NEWLINE tokens are significant as statement separators.

---

## Statement separation rules

Statements **must** be separated by one of:

* a semicolon `;`, OR
* a newline (i.e. a NEWLINE token), OR
* the end of a block `}` (closing brace) which terminates the last statement implicitly.

Examples of valid separations:

```dlba
print 0; print 1
print 0
print 1
print 0;
print 1
```

Invalid (syntax error):

```dlba
print 0 print 1   // missing separator
```

Parser enforces the terminator rule and will report an error like:

```
Expected ';' or newline after statement but got IDENT at file.dlba:12:5
```

which includes filename, line and column.

---

## High-level constructs and examples

* **Variable declaration:** `let x = 10`
* **Assignment:** `x = x + 1` (reassignment allowed; `let` required only for first declaration)
* **Function:**

```dlba
func add(a, b) {
  return a + b
}
```

* **Call:** `add(1, 2)`
* **If / Elif / Else:**

```dlba
if (x < 5) { ... } elif (x < 10) { ... } else { ... }
```

* **While:** `while (cond) { ... }`
* **Print:** `print("hello")` or `print "hello"` (parser accepts both parentheses and bare expr)
* **Modules:**

  * `import "utils.dlba"` — legacy: imports top-level names into current env
  * `import "utils.dlba" as utils` — binds a Module object to `utils` (use `utils.name` to access)
  * `from "math.dlba" import PI, add` — imports named symbols into current env

---

## Collections

* **List literal:** `[expr{, expr}]` e.g. `[1, 2, 3]`
* **Dict literal:** `{ (STRING|IDENT) : expr { , (STRING|IDENT) : expr } }` e.g. `{"a":1, b:2}` (IDENT keys become strings)
* **Indexing:** `a[0]`, `m["key"]`

---

## Operators and precedence (high → low)

1. **postfix**: call `()` , member access `.`, index `[]` (left-to-right)
2. **unary**: `!` `-` (right-to-left)
3. **multiplicative**: `* / %` (left-to-right)
4. **additive**: `+ -` (left-to-right)
5. **comparison**: `< > <= >=` (left-to-right)
6. **equality**: `== !=`
7. **logical AND**: `&&` (also `and` keyword normalized to `&&`)
8. **logical OR**: `||` (also `or` keyword normalized to `||`)

Notes:

* The lexer normalizes `and`/`or`/`not` to `&&`/`||`/`!` respectively, so parser sees uniform operator tokens.
* `+` between string and non-string will convert non-string to string (string concatenation behavior implemented in interpreter).

---

## Grammar (EBNF-like)

```
program       := statement*

statement     := var_decl
               | assignment
               | print_stmt
               | if_stmt
               | while_stmt
               | func_decl
               | return_stmt
               | import_stmt
               | expr_stmt

var_decl      := "let" IDENT "=" expr
assignment    := IDENT "=" expr
print_stmt    := "print" ("(" expr ")" | expr)

import_stmt   := "import" STRING [ "as" IDENT ]
               | "from" STRING "import" IDENT { "," IDENT }

func_decl     := "func" IDENT "(" [param_list] ")" block
param_list    := IDENT { "," IDENT }
return_stmt   := "return" [ expr ]

if_stmt       := "if" "(" expr ")" block { "elif" "(" expr ")" block } [ "else" block ]
while_stmt    := "while" "(" expr ")" block
block         := "{" statement* "}"

expr_stmt     := expr

expr          := or_expr
or_expr       := and_expr { ("||" | "or") and_expr }
and_expr      := equality { ("&&" | "and") equality }
equality      := comparison { ("==" | "!=") comparison }
comparison    := additive { ("<" | ">" | "<=" | ">=") additive }
additive      := term { ("+" | "-") term }
term          := factor { ("*" | "/" | "%") factor }
factor        := ("!" | "not" | "-") factor | postfix
postfix       := primary { call | member | index }
call          := "(" [ arg_list ] ")"
member        := "." IDENT
index         := "[" expr "]"
arg_list      := expr { "," expr }
primary       := NUMBER | STRING | TRUE | FALSE | IDENT | "(" expr ")" | list_literal | dict_literal
list_literal  := "[" [ expr { "," expr } ] "]"
dict_literal  := "{" [ (STRING | IDENT) ":" expr { "," (STRING | IDENT) ":" expr } ] "}"
```

---

## Parser & runtime semantics notes

* **Terminators:** After parsing a statement (top-level or inside a block), parser expects either `SEMICOLON`, `NEWLINE`, `RBRACE`, or EOF. Otherwise it raises a parse error with file\:line\:col info.
* **Module loading:** Interpreter resolves import paths relative to the importing file, then CWD, then `modules/` directory. Loaded modules are cached to prevent re-execution and to detect circular imports.
* **from-import semantics:** `from "path" import name1, name2` binds only the specified names into the current environment; if a requested name is missing from the module, interpreter raises a clear error.
* **Builtins:** Standard library functions are registered into each new `Environment` by `interpreter.register_stdlib` as `NativeFunction` objects (e.g., `len`, `str`, `int`, `float`, `range`, `read_file`, `write_file`, `abs`, `min`, `max`). Builtins can be shadowed by user declarations.
* **Error reporting:** Runtime and parse errors include `filename:line:column` where possible. The interpreter prints the source line and a caret pointing at the column when available. Call stack frames include function name and function definition location.

---

## Examples

```dlba
// basic
let x = 10
print(x)

// function
func f(n) {
  if (n <= 1) { return 1 }
  return n * f(n-1)
}
print(f(5))

// modules
import "utils.dlba" as u
print(u.MODULE_NAME)

from "math_extra.dlba" import PI
print(PI)

// collections
let a = [1,2,3]
print(a[1])
let d = {k: 10, "s": 20}
print(d["s"])
```

---