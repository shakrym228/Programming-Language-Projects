from lexer import tokenize
from parser import Parser
from interpreter import exec_statement, Environment

def repl():
    print("DLBA 0.0 [demo version 0.0, 24 Tir 1404 (15 July 2025)].\nFor exit type 'exit' or 'quit'.")
    env = Environment()

    while True:
        try:
            line = input(">>> ")

            if line.strip() in ("exit", "quit"):
                break
            
            if not line.strip().endswith(";") and not line.strip().startswith("print"):
                line = "print(" + line.strip() + ");"

            tokens = tokenize(line)
            parser = Parser(tokens)
            program = parser.parse()

            for stmt in program:
                exec_statement(stmt, env)

        except Exception as e:
            print("❌ خطا:", e)

if __name__ == "__main__":
    repl()