# main.py
import sys
from lexer import tokenize
from parser import Parser
from interpreter import interpret
from env import Environment
from repl import repl

def run_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        code = f.read()
    tokens = tokenize(code)
    parser = Parser(tokens)
    statements = parser.parse()
    env = Environment()
    interpret(statements, env)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        repl()
