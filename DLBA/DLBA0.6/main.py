# main.py - entrypoint
import sys
from lexer import tokenize
from parser import Parser
from interpreter import interpret, get_call_stack
from env import Environment

def format_traceback(e):
    print("---- DLBA Runtime Error ----")
    # interpreter call stack
    try:
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
        interpret(statements, env, current_filename=filename)
    except Exception as e:
        format_traceback(e)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        # run repl
        from repl import repl
        repl()
