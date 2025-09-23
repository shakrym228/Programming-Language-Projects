# repl.py - simple REPL adapted for NEWLINE tokens
from parser import Parser

from env import Environment
from interpreter import interpret
from lexer import tokenize


def repl():
    env = Environment()
    print(
        "DLBA REPL[demo version (0.6), September 23 2025 (1404 Mehr 1)].\nFor exit type 'exit' or 'quit'."
    )
    buffer = ""
    while True:
        try:
            line = input("DLBA> ")
            if line.strip() in ("exit", "quit"):
                break
            buffer += line + "\n"
            try:
                tokens = tokenize(buffer, filename="<stdin>")
                parser = Parser(tokens)
                statements = parser.parse()
            except Exception as e:
                # if parser expected more input, continue reading; otherwise show error
                if "Unexpected end of input" in str(e):
                    continue
                # else real parse error
                raise
            interpret(statements, env, current_filename="<stdin>")
            buffer = ""
        except Exception as e:
            print("Error:", e)
            buffer = ""
