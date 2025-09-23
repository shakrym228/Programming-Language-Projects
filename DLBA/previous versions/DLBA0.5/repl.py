# repl.py
from lexer import tokenize
from parser import Parser
from interpreter import interpret
from env import Environment

def repl():
    env = Environment()
    print("DLBA REPL[demo version (0.5), September 20 2025 (1404 Shahrivar 29)].\nFor exit type 'exit' or 'quit'.")
    buffer = ""
    while True:
        try:
            line = input("DLBA>> ")
            if line.strip() in ("exit", "quit"):
                break
            # allow multi-line when braces/parens not balanced
            buffer += line + "\n"
            # quick heuristic: try to tokenize & parse; on failure, continue reading
            try:
                tokens = tokenize(buffer, filename="<stdin>")
                parser = Parser(tokens)
                statements = parser.parse()
            except Exception as e:
                # incomplete input? keep reading
                # For simplicity, if error message is unexpected end of input, continue
                if "Unexpected end of input" in str(e):
                    continue
                else:
                    # real parse error
                    raise
            # success:
            interpret(statements, env)
            buffer = ""
        except Exception as e:
            print("Error:", e)
            buffer = ""
