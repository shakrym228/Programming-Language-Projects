# DLBA 0.5 Language Grammar & Syntax

This document describes the syntax and grammar rules of the **DLBA programming language (v0.5)**.  
It is designed as a reference for developers who want to write, understand, or extend DLBA programs.

---

## Data Types

- **Integer**: whole numbers (`42`, `-10`)
- **Float**: decimal numbers (`3.14`, `0.5`)
- **String**: double-quoted (`"Hello"`, `"Line\nBreak"`)
- **Boolean**: `True`, `False`

---

## Variables

- Declaration with `let`:

  ```dlba
  let x = 10
  let y = 3.5
  let name = "DLBA"
  ```

- Reassignment without `let`:
  ```dlba
  x = x + 1
  name = name + " v0.5"
  ```

---

## Operators

- **Arithmetic**:

  - `+` addition or string concatenation
  - `-` subtraction
  - `*` multiplication
  - `/` division (always float)
  - `%` modulus (remainder)

- **Comparison**:

  - `<`, `>`, `<=`, `>=`, `==`, `!=`

- **Logical**:

  - `&&` or `and` → AND
  - `||` or `or` → OR
  - `!` or `not` → NOT

- **Unary**:
  - `-` negate number
  - `!` logical negation

---

## Control Flow

- **If / Elif / Else**

  ```dlba
  if (x < 5) {
      print("less than 5")
  } elif (x < 10) {
      print("between 5 and 10")
  } else {
      print("10 or more")
  }
  ```

- **While Loop**
  ```dlba
  let i = 0
  while (i < 5) {
      print(i)
      i = i + 1
  }
  ```

---

## Functions

- **Declaration**:

  ```dlba
  func greet(name) {
      print("Hello, " + name)
  }
  ```

- **Return values**:

  ```dlba
  func add(a, b) {
      return a + b
  }

  let result = add(3, 4)
  print(result)
  ```

- **Calling**:
  ```dlba
  greet("Mahdi")
  ```

---

## Modules

- **Importing another DLBA file**:
  ```dlba
  import "math.dlba"
  ```

---

## Comments

- Single-line:

  ```dlba
  # this is a comment
  ```

- Multi-line:
  ```dlba
  /*
    this is
    a multi-line comment
  */
  ```

---

## Print Statement

```dlba
print("Hello World")
print(x + 5)
print("Result: " + x)
```

---

## Grammar (EBNF-like)

```
program     := statement*

statement   := var_decl
             | assignment
             | print_stmt
             | if_stmt
             | while_stmt
             | func_decl
             | return_stmt
             | import_stmt
             | expr

var_decl    := "let" IDENT "=" expr
assignment  := IDENT "=" expr
print_stmt  := "print" ( "(" expr ")" | expr )

if_stmt     := "if" "(" expr ")" block
             { "elif" "(" expr ")" block }
             [ "else" block ]

while_stmt  := "while" "(" expr ")" block

func_decl   := "func" IDENT "(" [ param_list ] ")" block
param_list  := IDENT { "," IDENT }
return_stmt := "return" expr

import_stmt := "import" STRING

block       := "{" statement* "}"

expr        := or_expr
or_expr     := and_expr { ("||" | "or") and_expr }
and_expr    := equality { ("&&" | "and") equality }
equality    := comparison { ("==" | "!=") comparison }
comparison  := additive { ("<"|">"|"<="|">=") additive }
additive    := term { ("+"|"-") term }
term        := factor { ("*"|"/"|"%") factor }
factor      := ("!"|"not"|"-") factor | primary

primary     := NUMBER | FLOAT | STRING | TRUE | FALSE | IDENT | call | "(" expr ")"
call        := IDENT "(" [ arg_list ] ")"
arg_list    := expr { "," expr }
```
