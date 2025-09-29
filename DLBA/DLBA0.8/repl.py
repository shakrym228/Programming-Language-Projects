# repl.py - DLBA REPL with readline/history and stdlib registration (v0.8)
import os

try:
    import readline
except Exception:
    readline = None

from parser import Parser

from env import Environment
from interpreter import format_traceback, interpret, register_stdlib
from lexer import tokenize

HISTORY_FILE = os.path.expanduser("~/.dlba_history")


def repl():
    env = Environment()
    register_stdlib(env)
    if readline:
        try:
            readline.read_history_file(HISTORY_FILE)
        except FileNotFoundError:
            pass
    buffer = ""
    print("DLBA REPL (v0.8). Type 'exit' to quit.")
    while True:
        try:
            prompt = "DLBA> " if buffer == "" else "...> "
            line = input(prompt)
            if line.strip() in ("exit", "quit"):
                break
            buffer += line + "\n"
            try:
                toks = tokenize(buffer, filename="<stdin>")
                parser = Parser(toks)
                stmts = parser.parse()
            except Exception as e:
                if "Unexpected end of input" in str(e):
                    continue
                raise
            try:
                interpret(stmts, env, current_filename="<stdin>")
            except Exception as ei:
                format_traceback(ei)
            if readline:
                try:
                    readline.write_history_file(HISTORY_FILE)
                except Exception:
                    pass
            buffer = ""
        except Exception as e:
            print("Parse error:", e)
            buffer = ""
