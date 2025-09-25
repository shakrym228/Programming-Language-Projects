# main.py - entrypoint (v0.7)
import sys
from parser import Parser

from env import Environment

from interpreter import format_traceback, interpret, register_stdlib
from lexer import tokenize


def run_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            code = f.read()
        tokens = tokenize(code, filename=filename)
        parser = Parser(tokens)
        statements = parser.parse()
        env = Environment()
        register_stdlib(env)
        # make argv available via dlba module (if stdlib uses dlba['argv'])
        dlba_mod = env.get("dlba")
        dlba_mod["argv"] = sys.argv[2:]
        interpret(statements, env, current_filename=filename)
    except Exception as e:
        format_traceback(e)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        from repl import repl

        repl()
