# main.py - entrypoint with nicer error printing
import sys
import traceback
from lexer import tokenize
from parser import Parser
from interpreter import interpret, get_call_stack, _loaded_modules
from env import Environment
from repl import repl

def format_traceback(e):
    print("---- DLBA Runtime Error ----")
    # print Python traceback for debugging the interpreter error (optional)
    # print(traceback.format_exc())
    # Print interpreter call stack
    try:
        from interpreter import get_call_stack
        cs = get_call_stack()
        if cs:
            print("Call stack (most recent call last):")
            for name, filename, lineno in reversed(cs):
                print(f'  in {name} at {filename}:{lineno}')
    except Exception:
        pass
    print("Error:", e)

def run_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            code = f.read()
        tokens = tokenize(code, filename=filename)
        parser = Parser(tokens)
        statements = parser.parse()
        env = Environment()
        interpret(statements, env)
    except Exception as e:
        format_traceback(e)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        repl()
