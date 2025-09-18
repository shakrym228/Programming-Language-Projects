import re
import codecs

# Order matters: multi-char tokens and keywords before IDENT.

TOKEN_REGEX = [
    # numbers: floats first
    ('FLOAT',     r'\d+\.\d+'),
    ('NUMBER',    r'\d+'),

    # multi-char comparison / logical operators
    ('EQ',        r'=='),
    ('NE',        r'!='),
    ('LE',        r'<='),
    ('GE',        r'>='),

    # logical symbols
    ('ANDAND',    r'&&'),
    ('OROR',      r'\|\|'),

    # single-char operators
    ('LT',        r'<'),
    ('GT',        r'>'),
    ('PLUS',      r'\+'),
    ('MINUS',     r'-'),
    ('STAR',      r'\*'),
    ('SLASH',     r'/'),
    ('BANG',      r'!'),

    # assignment and punctuation
    ('ASSIGN',    r'='),
    ('SEMICOLON', r';'),
    ('LPAREN',    r'\('),
    ('RPAREN',    r'\)'),
    ('LBRACE',    r'\{'),
    ('RBRACE',    r'\}'),

    # string literal (double quotes, supports simple escapes)
    ('STRING',    r'"(?:\\.|[^"\\])*"'),

    # keywords (use word boundaries)
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

    # identifier (after keywords)
    ('IDENT',     r'[A-Za-z_][A-Za-z0-9_]*'),

    # whitespace / newline
    ('NEWLINE',   r'\n'),
    ('SKIP',      r'[ \t\r]+'),

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

def _unescape_string(s):
    # input s includes surrounding quotes
    inner = s[1:-1]
    # decode common escapes like \n, \t, \", \\ etc.
    return codecs.decode(inner, 'unicode_escape')

def tokenize(code):
    tokens = []
    for match in MASTER_RE.finditer(code):
        kind = match.lastgroup
        text = match.group()
        if kind == 'FLOAT':
            tokens.append(Token('NUMBER', float(text)))
        elif kind == 'NUMBER':
            tokens.append(Token('NUMBER', int(text)))
        elif kind == 'STRING':
            tokens.append(Token('STRING', _unescape_string(text)))
        elif kind in ('EQ','NE','LE','GE','LT','GT','PLUS','MINUS','STAR','SLASH','BANG'):
            tokens.append(Token('OP', text))
        elif kind in ('ANDAND','OROR'):
            tokens.append(Token('OP', text))  # '&&' or '||'
        elif kind in ('AND','OR','NOT'):
            # also accept keywords and/or/not
            canonical = {'AND':'&&', 'OR':'||', 'NOT':'!'}[kind]
            tokens.append(Token('OP', canonical))
        elif kind in ('ASSIGN','SEMICOLON','LPAREN','RPAREN','LBRACE','RBRACE'):
            tokens.append(Token(kind, text))
        elif kind in ('IF','ELSE','WHILE','PRINT','LET','ELIF','TRUE','FALSE'):
            tokens.append(Token(kind, text))
        elif kind == 'IDENT':
            tokens.append(Token('IDENT', text))
        elif kind in ('NEWLINE','SKIP'):
            continue
        elif kind == 'MISMATCH':
            raise Exception(f"Unexpected character: {text}")
    return tokens
