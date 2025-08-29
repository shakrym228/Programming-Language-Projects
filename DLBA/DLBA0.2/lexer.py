import re

# Token specification (order matters: multi-char tokens and keywords before IDENT)
TOKEN_REGEX = [
    ('NUMBER',    r'\d+'),

    # multi-char comparison operators first
    ('EQ',        r'=='),
    ('NE',        r'!='),
    ('LE',        r'<='),
    ('GE',        r'>='),

    # single-char comparisons and arithmetic
    ('LT',        r'<'),
    ('GT',        r'>'),
    ('PLUS',      r'\+'),
    ('MINUS',     r'-'),
    ('STAR',      r'\*'),
    ('SLASH',     r'/'),

    # assignment (single =), semicolon, parens, braces
    ('ASSIGN',    r'='),
    ('SEMICOLON', r';'),
    ('LPAREN',    r'\('),
    ('RPAREN',    r'\)'),
    ('LBRACE',    r'\{'),
    ('RBRACE',    r'\}'),

    # keywords (use word boundaries so IDENT doesn't eat them)
    ('IF',        r'\bif\b'),
    ('ELSE',      r'\belse\b'),
    ('WHILE',     r'\bwhile\b'),
    ('PRINT',     r'\bprint\b'),
    ('LET',       r'\blet\b'),
    ('TRUE',      r'\btrue\b'),
    ('FALSE',     r'\bfalse\b'),

    # identifier (after keywords)
    ('IDENT',     r'[A-Za-z_][A-Za-z0-9_]*'),

    # whitespace / newline
    ('NEWLINE',   r'\n'),
    ('SKIP',      r'[ \t]+'),

    # anything else
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
    tokens = []
    for match in MASTER_RE.finditer(code):
        kind = match.lastgroup
        text = match.group()
        if kind == 'NUMBER':
            value = int(text)
            tokens.append(Token('NUMBER', value))
        elif kind in ('EQ','NE','LE','GE','LT','GT','PLUS','MINUS','STAR','SLASH'):
            tokens.append(Token('OP', text))
        elif kind == 'ASSIGN':
            tokens.append(Token('ASSIGN', text))
        elif kind == 'SEMICOLON':
            tokens.append(Token('SEMICOLON', text))
        elif kind in ('LPAREN','RPAREN','LBRACE','RBRACE'):
            tokens.append(Token(kind, text))
        elif kind in ('IF','ELSE','WHILE','PRINT','LET','TRUE','FALSE'):
            tokens.append(Token(kind, text))
        elif kind == 'IDENT':
            tokens.append(Token('IDENT', text))
        elif kind in ('NEWLINE','SKIP'):
            continue
        elif kind == 'MISMATCH':
            raise Exception(f"Unexpected character: {text}")
    return tokens
