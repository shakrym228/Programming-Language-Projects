from lexer import tokenize
from parser import Parser
from interpreter import interpret
from env import Environment

def repl():
    env = Environment()
    print("DLBA REPL[demo version (0.2), 6 Shahrivar 1404 (28 August 2025)].\nFor exit type 'exit' or 'quit'.")
    while True:
        try:
            line = input("DLBA>> ")
            if line.strip() in ("exit", "quit"):
                break
            tokens = tokenize(line)
            parser = Parser(tokens)
            statements = parser.parse()
            interpret(statements, env)
        except Exception as e:
            print("Error:", e)
if __name__ == "__main__":
    repl()