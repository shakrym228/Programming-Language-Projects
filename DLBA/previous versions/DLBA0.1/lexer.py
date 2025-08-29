import re

TOKEN_REGEX = [

    # عملگرهای مقایسه‌ای (اولویت بالاتر)
    ('EQ',        r'=='),
    ('NE',        r'!='),
    ('LE',        r'<='),
    ('GE',        r'>='),
    ('LT',        r'<'),
    ('GT',        r'>'),

    ('IF',        r'\bif\b'),
    ('ELSE',      r'\belse\b'),
    ('PRINT',     r'\bprint\b'),
    ('LET',       r'\blet\b'),

    ('NUMBER',    r'\d+'),
    ('IDENT',     r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('ASSIGN',    r'='),
    ('PLUS',      r'\+'),
    ('MINUS',     r'-'),
    ('STAR',      r'\*'),
    ('SLASH',     r'/'),
    ('LPAREN',    r'\('),
    ('RPAREN',    r'\)'),
    ('LBRACE',    r'\{'),
    ('RBRACE',    r'\}'),
    ('SEMICOLON', r';'),
    ('NEWLINE',   r'\n'),
    ('SKIP',      r'[ \t]+'),
]

MASTER_REGEX = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_REGEX)
class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f'Token({self.type}, {self.value})'

def tokenize(code):
    tokens = []
    for match in re.finditer(MASTER_REGEX, code):
        kind = match.lastgroup
        text = match.group()
        if kind == 'NUMBER':
            value = int(text)
        else:
            value = text
        if kind in ('SKIP', 'NEWLINE'):
            continue
        tokens.append(Token(kind, value))
    return tokens