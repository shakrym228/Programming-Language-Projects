from lexer import tokenize
from parser import Parser
from interpreter import Environment, exec_statement

def repl():
    env = Environment()
    print("DLBA [demo version 0.1, 28 Tir 1404 (19 July 2025)].\nFor exit type 'exit' or 'quit'.")
    while True:
        try:
            line = input(">>> ")
            line = line.strip()
            if line in ("quit", "exit"):
                break
            if not line.endswith(";") and not line.startswith("print") and not line.startswith("if") and not line.startswith("let"):
                line = "print(" + line + ");"

                
            tokens = tokenize(line)
            parser = Parser(tokens)
            statements = parser.parse()
            for stmt in statements:
                exec_statement(stmt, env)
        except Exception as e:
            print("❌ خطا:", e)
            
if __name__ == "__main__":
    repl()