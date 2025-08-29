import sys
from repl import repl
from lexer import tokenize
from parser import Parser
from interpreter import Environment, exec_statement

def run_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        code = f.read()
    tokens = tokenize(code)
    parser = Parser(tokens)
    statements = parser.parse()
    env = Environment()
    for stmt in statements:
        exec_statement(stmt, env)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        repl()