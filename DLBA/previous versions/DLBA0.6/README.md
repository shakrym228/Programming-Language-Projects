# DLBA Programming Language

**Release date:** (September 23, 2025)
**Author:** Mahdi Shakeri

---

## 📖 Introduction

DLBA is a lightweight experimental programming language written in Python. It is designed as a learning project to understand how interpreters and compilers work, while gradually adding real programming features such as variables, loops, conditionals, functions, and modules.

DLBA source files use the `.dlba` extension and can be executed through the interpreter (`main.py`).

---

## ✨ Features (v0.6)

- **Variables & Assignments** (`x = 10`)
- **Arithmetic & Boolean Expressions**
- **Conditionals** (`if` / `else`)
- **Loops** (`while`)
- **Functions** with parameters and return values
- **Modules** with `import` support
- **Improved Error Handling** with line numbers and runtime error messages
- **Semicolon Support** (multiple statements per line)
- **Multi-line Programs** with clear parsing of newlines

---

## 📝 Syntax (Highlights)

```dlba
# Variables
x = 42

# Conditionals
if (x > 10) {
    print("Large")
} else {
    print("Small")
}

# Loop
while (x > 0) {
    x = x - 1
}

# Functions
func add(a, b) {
    return a + b
}

print(add(5, 7))

# Importing a module
import utils
print(utils.square(6))
```

---

## ⚠️ Error Handling

Errors are reported with detailed messages including the **line number**:

```
---- DLBA Runtime Error ----
Error: Division by zero at example.dlba:12
```

---

## 🛠️ Roadmap

- **v0.7**: Arrays & Strings
- **v0.8**: Standard Library (math, io)
- **v0.9**: REPL improvements, debugging tools
- **v1.0**: Stable core with documentation and examples

---

Run any `.dlba` file:

```bash
python main.py myfile.dlba
```

---

## ▶️ Usage

Example:

```bash
python main.py tests/main_test_v0_6_full.dlba
```

---

## 💡 Examples

See the `tests/` directory for usage examples:

- `main_test_v0_6_full.dlba` → Full language feature test
- `utils.dlba` → Utility functions
- `math_extra.dlba` → Extra math functions

---

## 🤝 Contributing

This is a learning project. Contributions are welcome for improvements, new features, and documentation.

---
