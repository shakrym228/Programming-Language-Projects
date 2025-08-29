from lexer import tokenize
from parser import Parser
from interpreter import interpret

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        with open(filename, 'r') as f:
            content = f.read()
        interpret(Parser(tokenize(content)).parse())
    else:
        import subprocess
        subprocess.run(['python', 'repl.py'])