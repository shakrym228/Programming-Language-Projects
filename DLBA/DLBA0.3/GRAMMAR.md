# DLBA 0.3 Language Grammar & Syntax

This document describes the syntax and grammar rules of the **DLBA programming language (v0.3)**.  
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

- Reassignment without `let`:
  x = x + 1
  name = name + " v0.3"

## Operators
- Arithmetic:

  '+' addition or string concatenation

  '-' subtraction

  '*' multiplication

  '/' division (always float)

- Comparison

  <, >, <=, >=, ==, !=

- Logical

  && or and → AND

  || or or → OR

 ! or not → NOT

- Unary

  '-' negate number

  ! logical negation

## Control Flow
- If / Elif / Else

  if (x < 5) {
      print("less than 5")
  } elif (x < 10) {
      print("between 5 and 10")
  } else {
      print("10 or more")
  }

- While Loop

  let i = 0
  while (i < 5) {
      print(i)
      i = i + 1
  }

## Print Statement
  print("Hello World")
  print(x + 5)
  print("Result: " + x)

## Grammar (EBNF-like)
  program     := statement*

  statement   := var_decl
               | assignment
               | print_stmt
               | if_stmt
               | while_stmt

  var_decl    := "let" IDENT "=" expr
  assignment  := IDENT "=" expr
  print_stmt  := "print" ( "(" expr ")" | expr )

  if_stmt     := "if" "(" expr ")" block
               { "elif" "(" expr ")" block }
               [ "else" block ]

  while_stmt  := "while" "(" expr ")" block

  block       := "{" statement* "}"

  expr        := or_expr
  or_expr     := and_expr { ("||" | "or") and_expr }
  and_expr    := equality { ("&&" | "and") equality }
  equality    := comparison { ("==" | "!=") comparison }
  comparison  := additive { ("<"|">"|"<="|">=") additive }
  additive    := term { ("+"|"-") term }
  term        := factor { ("*"|"/") factor }
  factor      := ("!"|"not"|"-") factor | primary

  primary     := NUMBER | FLOAT | STRING | TRUE | FALSE | IDENT | "(" expr ")"