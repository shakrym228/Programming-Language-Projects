# DLBA 0.4 Language Grammar & Syntax

This document describes the syntax and grammar rules of the **DLBA programming language (v0.4)**.  
It is designed as a copy‑friendly reference for developers who want to write, understand, or extend DLBA programs.

---

## Data Types
- **Integer**: whole numbers (`42`, `-10`)  
- **Float**: decimal numbers (`3.14`, `0.5`)  
- **String**: double-quoted (`"Hello"`, `"Line\nBreak"`)  
- **Boolean**: `True`, `False`

---

## Comments
- **Single-line**: start with `//` and continue to the end of the line.
  ```dlba
  // This is a single-line comment
  let x = 5 // comment after code
  ```
- **Multi-line**: `/* ... */` can span multiple lines.
  ```dlba
  /* This is a
     multi-line comment */
  ```
Comments inside string literals are **not** treated as comments.

---

## Variables
- Declaration with `let`:
  ```dlba
  let x = 10
  let y = 3.5
  let name = "DLBA"
  ```
- Reassignment without `let` (allowed only if the variable exists or will be declared by `let` first):
  ```dlba
  x = x + 1
  name = name + " v0.4"
  ```
- Semicolons are optional; both `let x = 5` and `let x = 5;` are accepted.

---

## Operators
### Arithmetic
- `+` addition or string concatenation
- `-` subtraction
- `*` multiplication
- `/` division (true division; returns float when necessary)
- `%` modulus (remainder)

### Comparison
- `<`, `>`, `<=`, `>=`, `==`, `!=`

### Logical
- `&&` or keyword `and` → logical AND  
- `||` or keyword `or` → logical OR  
- `!` or keyword `not` → logical NOT

### Unary
- `-` numeric negation  
- `!` logical negation

---

## Control Flow
### If / Elif / Else
```dlba
if (x < 5) {
    print("less than 5")
} elif (x < 10) {
    print("between 5 and 10")
} else {
    print("10 or more")
}
```

### While Loop
```dlba
let i = 0
while (i < 5) {
    print(i)
    i = i + 1
}
```

---

## Functions
- **Definition**:
  ```dlba
  func add(a, b) {
      return a + b
  }
  ```
- **Call**:
  ```dlba
  let result = add(2, 3)
  print(result)
  ```
- `return` exits the function and optionally returns a value. If no `return` is executed explicitly, the function returns `None`.
- Functions use lexical scoping: a function captures the environment at definition time (closures supported).

---

## Print Statement
Supports either `print(expr)` or `print expr`:
```dlba
print("Hello World")
print(x + 5)
print("Result: " + x)
```
String concatenation with `+` will implicitly convert numbers and booleans to strings.

---

## Grammar (EBNF-like)
```
program     := statement*

statement   := var_decl
             | func_def
             | assignment
             | print_stmt
             | return_stmt
             | if_stmt
             | while_stmt
             | expr_stmt

var_decl    := "let" IDENT "=" expr [";"]
assignment  := IDENT "=" expr [";"]
func_def    := "func" IDENT "(" params? ")" block
params      := IDENT ("," IDENT)*
print_stmt  := "print" ("(" expr ")" | expr) [";"]
return_stmt := "return" expr? [";"]
if_stmt     := "if" "(" expr ")" block
               ("elif" "(" expr ")" block)*
               ["else" block]
while_stmt  := "while" "(" expr ")" block
expr_stmt   := expr [";"]
block       := "{" statement* "}"

# Expressions (precedence from low to high)
expr        := or_expr
or_expr     := and_expr ( ("||" | "or") and_expr )*
and_expr    := equality ( ("&&" | "and") equality )*
equality    := comparison ( ("==" | "!=") comparison )*
comparison  := additive ( ("<" | ">" | "<=" | ">=") additive )*
additive    := term ( ("+" | "-") term )*
term        := factor ( ("*" | "/" | "%") factor )*
factor      := ("!" | "-") factor | primary
primary     := NUMBER | STRING | TRUE | FALSE | IDENT | IDENT "(" args? ")" | "(" expr ")"
args        := expr ("," expr)*
```

---

## Examples (covering v0.4 features)
```dlba
// comments
/* multi-line
   comment */

let a = 5
let b = 2.5
print(a + b)

let s = "Hello"
print(s + " DLBA")

// logical and comparisons
if (a > b) {
    print("a is greater")
} elif (a == b) {
    print("a equals b")
} else {
    print("a is smaller")
}

// modulus and while
let i = 0
let sum = 0
while (i < 5) {
    sum = sum + i
    i = i + 1
}
print("sum % 3 = " + (sum % 3))

// functions and return
func factorial(n) {
    if (n <= 1) {
        return 1
    } else {
        return n * factorial(n - 1)
    }
}
print(factorial(5))
```

---

