import re

# تعریف انواع توکن‌ها
TOKEN_TYPES = [
    ("LET",       r"\blet\b"),
    ("PRINT",     r"\bprint\b"),
    ("NUMBER",    r"\d+"),
    ("IDENT",     r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("EQUAL",     r"="),
    ("PLUS",      r"\+"),
    ("MINUS",     r"-"),
    ("MULT",      r"\*"),
    ("DIV",       r"/"),
    ("LPAREN",    r"\("),
    ("RPAREN",    r"\)"),
    ("SEMICOLON", r";"),
    ("WHITESPACE",r"[ \t\n]+"),
]

def tokenize(code):
    pos = 0
    tokens = []
    while pos < len(code):
        match_found = False
        for tok_type, regex in TOKEN_TYPES:
            pattern = re.compile(regex)
            match = pattern.match(code, pos)
            if match:
                value = match.group(0)
                if tok_type != "WHITESPACE":
                    tokens.append({"type": tok_type, "value": value})
                pos = match.end()
                match_found = True
                break
        if not match_found:
            raise Exception(f"خطای لغوی: کاراکتر نامعتبر در موقعیت {pos}: {code[pos]}")
    return tokens