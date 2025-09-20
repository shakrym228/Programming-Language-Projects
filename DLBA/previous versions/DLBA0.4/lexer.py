# lexer.py
import re

# We'll implement comment stripping that respects string literals.
def strip_comments(code):
    result = []
    i = 0
    n = len(code)
    in_string = False
    string_char = None
    while i < n:
        ch = code[i]
        # handle string start/end and escapes
        if in_string:
            if ch == '\\' and i + 1 < n:
                # keep escape and next char
                result.append(code[i])
                result.append(code[i+1])
                i += 2
                continue
            elif ch == string_char:
                in_string = False
                string_char = None
                result.append(ch)
                i += 1
                continue
            else:
                result.append(ch)
                i += 1
                continue
        else:
            # not in string
            if ch == '"' or ch == "'":
                in_string = True
                string_char = ch
                result.append(ch)
                i += 1
                continue
            # single-line comment //
            if ch == '/' and i + 1 < n and code[i+1] == '/':
                # skip until end of line but keep newline
                i += 2
                while i < n and code[i] != '\n':
                    i += 1
                continue
            # multi-line comment /* ... */
            if ch == '/' and i + 1 < n and code[i+1] == '*':
                i += 2
                while i + 1 < n and not (code[i] == '*' and code[i+1] == '/'):
                    i += 1
                i += 2 if i + 1 < n else 1
                continue
            # normal char
            result.append(ch)
            i += 1
    return ''.join(result)

# Token specifications (order matters)
TOKEN_REGEX = [
    ('FLOAT',     r'\d+\.\d+'),
    ('NUMBER',    r'\d+'),

    # multi-char comparison / equality operators
    ('EQ',        r'=='),
    ('NE',        r'!='),
    ('LE',        r'<='),
    ('GE',        r'>='),

    # logical multi-char
    ('ANDAND',    r'&&'),
    ('OROR',      r'\|\|'),

    # single-char operators and modulus
    ('LT',        r'<'),
    ('GT',        r'>'),
    ('PLUS',      r'\+'),
    ('MINUS',     r'-'),
    ('STAR',      r'\*'),
    ('SLASH',     r'/'),
    ('MOD',       r'%'),
    ('BANG',      r'!'),

    # punctuation
    ('ASSIGN',    r'='),
    ('SEMICOLON', r';'),
    ('COMMA',     r','),
    ('LPAREN',    r'\('),
    ('RPAREN',    r'\)'),
    ('LBRACE',    r'\{'),
    ('RBRACE',    r'\}'),

    # strings
    ('STRING',    r'"(?:\\.|[^"\\])*"'),

    # keywords
    ('FUNC',      r'\bfunc\b'),
    ('RETURN',    r'\breturn\b'),
    ('ELIF',      r'\belif\b'),
    ('IF',        r'\bif\b'),
    ('ELSE',      r'\belse\b'),
    ('WHILE',     r'\bwhile\b'),
    ('PRINT',     r'\bprint\b'),
    ('LET',       r'\blet\b'),
    ('TRUE',      r'\bTrue\b'),
    ('FALSE',     r'\bFalse\b'),
    ('AND',       r'\band\b'),
    ('OR',        r'\bor\b'),
    ('NOT',       r'\bnot\b'),

    # identifier
    ('IDENT',     r'[A-Za-z_][A-Za-z0-9_]*'),

    ('NEWLINE',   r'\n'),
    ('SKIP',      r'[ \t\r]+'),
    ('MISMATCH',  r'.'),
]

MASTER_REGEX = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_REGEX)
MASTER_RE = re.compile(MASTER_REGEX)

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"

def tokenize(code):
    cleaned = strip_comments(code)
    tokens = []
    for match in MASTER_RE.finditer(cleaned):
        kind = match.lastgroup
        text = match.group()
        if kind == 'FLOAT':
            tokens.append(Token('NUMBER', float(text)))
        elif kind == 'NUMBER':
            tokens.append(Token('NUMBER', int(text)))
        elif kind == 'STRING':
            # remove surrounding quotes and unescape
            s = text[1:-1]
            s = bytes(s, "utf-8").decode("unicode_escape")
            tokens.append(Token('STRING', s))
        elif kind in ('EQ','NE','LE','GE','LT','GT','PLUS','MINUS','STAR','SLASH','MOD','BANG'):
            tokens.append(Token('OP', text))
        elif kind in ('ANDAND','OROR'):
            tokens.append(Token('OP', text))
        elif kind in ('AND','OR','NOT'):
            canonical = {'AND':'&&','OR':'||','NOT':'!'}[kind]
            tokens.append(Token('OP', canonical))
        elif kind in ('ASSIGN','SEMICOLON','COMMA','LPAREN','RPAREN','LBRACE','RBRACE'):
            tokens.append(Token(kind, text))
        elif kind in ('FUNC','RETURN','ELIF','IF','ELSE','WHILE','PRINT','LET','TRUE','FALSE'):
            tokens.append(Token(kind, text))
        elif kind == 'IDENT':
            tokens.append(Token('IDENT', text))
        elif kind in ('NEWLINE','SKIP'):
            continue
        elif kind == 'MISMATCH':
            raise Exception(f"Unexpected character: {text}")
    return tokens
