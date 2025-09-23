# DLBA Programming Language – Version 0.5

**Release date:** 2025-09-20  
**Author:** Mahdi Shakeri

---

## 📖 Introduction

DLBA is a custom programming language created step by step as a learning and research project. Each version introduces new features and improvements while keeping the language simple and educational.

This document provides an overview of **version 0.5**, its features, structure, and usage.

---

## 🚀 What’s New in v0.5

- **Modules / Import System**

  - Import other `.dlba` files using `import "utils.dlba"`.
  - Imports are idempotent (re-importing does not re-run the code).
  - Circular imports are detected and reported.

- **Advanced Error Reporting**

  - Errors now show filename and line number.
  - Call stack is displayed for runtime errors.

- **Preserved Features from v0.4**
  - Variables (`let`, reassignment without `let`).
  - Data types: integers, floats, strings, booleans.
  - Operators: arithmetic (`+ - * / %`), comparisons, logical (`&& || !`).
  - Control flow: `if / elif / else`, `while` loops.
  - Functions with arguments and return values.
  - Recursion supported.
  - Comments: `// single-line`, `/* multi-line */`.

---

## 🗂 Project Structure

- `lexer.py` – Tokenizer with comment removal and line/file tracking.
- `parser.py` – Parser producing AST nodes.
- `ast_nodes.py` – Abstract Syntax Tree (AST) classes.
- `interpreter.py` – Core interpreter with call stack and module loader.
- `env.py` – Environment with lexical scoping.
- `main.py` – File runner with error handling.
- `repl.py` – Interactive REPL for experimenting.
- Example modules: `utils.dlba`, `math_extra.dlba`.
- Full test file: `main_test_v0_5.dlba`.

---

## 🧪 Testing v0.5

1. Place all files in one folder:

   ```
   lexer.py parser.py ast_nodes.py interpreter.py env.py main.py repl.py
   utils.dlba math_extra.dlba main_test_v0_5.dlba
   ```

2. Run the main test:

   ```bash
   python main.py main_test_v0_5.dlba
   ```

3. To check error stack trace, uncomment this line inside `main_test_v0_5.dlba`:
   ```dlba
   safe_div(10, 0)
   ```

---

## 📚 Example Code

```dlba
import "utils.dlba"
import "math_extra.dlba"

func factorial(n) {
    if (n <= 1) {
        return 1
    } else {
        return n * factorial(n - 1)
    }
}

print("factorial(5) ->"); print(factorial(5))
print("add(2,3) ->"); print(add(2,3))
```

---

## 🔮 Future Plans (v0.6+)

- Namespaced imports (`import "utils.dlba" as utils`).
- Dot operator for module members (`utils.inc(5)`).
- Data collections: lists, dictionaries.
- Extended standard library.
- Enhanced REPL (history, multiline editing).
- Automated test harness.

---

## 🤝 Contribution

- Add test files in a `tests/` directory.
- Report issues or suggest improvements.
- Keep contributions modular and well-documented.

---

✨ **Enjoy exploring DLBA v0.5!** ✨
