# lexer.py - DLBA lexer (v0.8 - same as v0.7)
import re

SOURCE_MAP = {}

# token spec as in v0.7 (kept identical)
TOKEN_SPEC = [
    ("FLOAT", r"\d+\.\d+"),
    ("NUMBER", r"\d+"),
    ("EQ", r"=="),
    ("NE", r"!="),
    ("LE", r"<="),
    ("GE", r">="),
    ("ANDAND", r"&&"),
    ("OROR", r"\|\|"),
    ("LT", r"<"),
    ("GT", r">"),
    ("PLUS", r"\+"),
    ("MINUS", r"-"),
    ("STAR", r"\*"),
    ("SLASH", r"/"),
    ("MOD", r"%"),
    ("BANG", r"!"),
    ("ASSIGN", r"="),
    ("SEMICOLON", r";"),
    ("COMMA", r","),
    ("COLON", r":"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("LBRACE", r"\{"),
    ("RBRACE", r"\}"),
    ("LBRACK", r"\["),
    ("RBRACK", r"\]"),
    ("DOT", r"\."),
    ("STRING", r'"(?:\\.|[^"\\])*"'),
    ("FROM", r"\bfrom\b"),
    ("IMPORT", r"\bimport\b"),
    ("AS", r"\bas\b"),
    ("FUNC", r"\bfunc\b"),
    ("RETURN", r"\breturn\b"),
    ("ELIF", r"\belif\b"),
    ("IF", r"\bif\b"),
    ("ELSE", r"\belse\b"),
    ("WHILE", r"\bwhile\b"),
    ("PRINT", r"\bprint\b"),
    ("LET", r"\blet\b"),
    ("TRUE", r"\b(True|true)\b"),
    ("FALSE", r"\b(False|false)\b"),
    ("AND", r"\band\b"),
    ("OR", r"\bor\b"),
    ("NOT", r"\bnot\b"),
    ("IDENT", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("NEWLINE", r"\n"),
    ("SKIP", r"[ \t\r]+"),
    ("MISMATCH", r"."),
]

MASTER_RE = re.compile("|".join(f"(?P<{name}>{pat})" for name, pat in TOKEN_SPEC))


class Token:
    def __init__(self, type_, value=None, lineno=None, col=None, filename=None):
        self.type = type_
        self.value = value
        self.lineno = lineno
        self.col = col
        self.filename = filename

    def __repr__(self):
        return f"Token({self.type}, {self.value}, {self.filename}:{self.lineno}:{self.col})"


# tokenize function identical to v0.7 implementation (use the corrected version previously provided)
def tokenize(code, filename="<input>"):
    # store original source lines (use raw code so reported line numbers match file)
    SOURCE_MAP[filename] = code.splitlines()

    def strip_comments(code):
        result = []
        i = 0
        n = len(code)
        in_string = False
        string_char = None
        while i < n:
            ch = code[i]
            if in_string:
                if ch == "\\" and i + 1 < n:
                    result.append(code[i])
                    result.append(code[i + 1])
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
                if ch == '"' or ch == "'":
                    in_string = True
                    string_char = ch
                    result.append(ch)
                    i += 1
                    continue
                if ch == "/" and i + 1 < n and code[i + 1] == "/":
                    i += 2
                    while i < n and code[i] != "\n":
                        i += 1
                    continue
                if ch == "/" and i + 1 < n and code[i + 1] == "*":
                    start = i
                    i += 2
                    while i + 1 < n and not (code[i] == "*" and code[i + 1] == "/"):
                        i += 1
                    end = i + 2 if i + 1 < n else i
                    comment_text = code[start:end]
                    newline_count = comment_text.count("\n")
                    result.append("\n" * newline_count)
                    i = end
                    continue
                result.append(ch)
                i += 1
        return "".join(result)

    cleaned = strip_comments(code)
    tokens = []
    lineno = 1
    col = 1
    for m in MASTER_RE.finditer(cleaned):
        kind = m.lastgroup
        text = m.group()
        token_lineno = lineno
        token_col = col

        if kind == "NEWLINE":
            tokens.append(Token("NEWLINE", text, token_lineno, token_col, filename))
            lineno += 1
            col = 1
            continue

        newlines = text.count("\n")
        if newlines:
            last_nl = text.rfind("\n")
            lineno += newlines
            col = len(text) - last_nl
        else:
            col += len(text)

        if kind == "FLOAT":
            tokens.append(
                Token("NUMBER", float(text), token_lineno, token_col, filename)
            )
        elif kind == "NUMBER":
            tokens.append(Token("NUMBER", int(text), token_lineno, token_col, filename))
        elif kind == "STRING":
            inner = text[1:-1]
            inner = bytes(inner, "utf-8").decode("unicode_escape")
            tokens.append(Token("STRING", inner, token_lineno, token_col, filename))
        elif kind in (
            "EQ",
            "NE",
            "LE",
            "GE",
            "LT",
            "GT",
            "PLUS",
            "MINUS",
            "STAR",
            "SLASH",
            "MOD",
            "BANG",
        ):
            tokens.append(Token("OP", text, token_lineno, token_col, filename))
        elif kind in ("ANDAND", "OROR"):
            tokens.append(Token("OP", text, token_lineno, token_col, filename))
        elif kind in ("AND", "OR", "NOT"):
            canonical = {"AND": "&&", "OR": "||", "NOT": "!"}[kind]
            tokens.append(Token("OP", canonical, token_lineno, token_col, filename))
        elif kind == "DOT":
            tokens.append(Token("DOT", text, token_lineno, token_col, filename))
        elif kind in (
            "ASSIGN",
            "SEMICOLON",
            "COMMA",
            "COLON",
            "LPAREN",
            "RPAREN",
            "LBRACE",
            "RBRACE",
            "LBRACK",
            "RBRACK",
        ):
            tokens.append(Token(kind, text, token_lineno, token_col, filename))
        elif kind in (
            "FROM",
            "IMPORT",
            "AS",
            "FUNC",
            "RETURN",
            "ELIF",
            "IF",
            "ELSE",
            "WHILE",
            "PRINT",
            "LET",
        ):
            tokens.append(Token(kind, text, token_lineno, token_col, filename))
        elif kind in ("TRUE", "FALSE"):
            val = True if text.lower() == "true" else False
            tokens.append(
                Token(
                    "TRUE" if val else "FALSE", val, token_lineno, token_col, filename
                )
            )
        elif kind == "IDENT":
            tokens.append(Token("IDENT", text, token_lineno, token_col, filename))
        elif kind == "SKIP":
            continue
        elif kind == "MISMATCH":
            raise Exception(
                f"Unexpected character {text} at {filename}:{token_lineno}:{token_col}"
            )
    return tokens
