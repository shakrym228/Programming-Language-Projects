# تعریف گره‌های AST

class Number:
    def __init__(self, value):
        self.value = int(value)

class Identifier:
    def __init__(self, name):
        self.name = name

class BinaryOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Assignment:
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

class Print:
    def __init__(self, expr):
        self.expr = expr

# کلاس Parser

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else {"type": "EOF", "value": ""}

    def match(self, expected_type):
        if self.current()["type"] == expected_type:
            self.pos += 1
            return True
        return False

    def consume(self, expected_type):
        if not self.match(expected_type):
            raise Exception(f"انتظار داشتیم {expected_type} اما دریافت شد {self.current()}")
        return self.tokens[self.pos - 1]

    def parse(self):
        stmts = []
        while self.current()["type"] != "EOF":
            stmts.append(self.parse_statement())
        return stmts

    def parse_statement(self):
        if self.match("LET"):
            name = self.consume("IDENT")["value"]
            self.consume("EQUAL")
            expr = self.parse_expression()
            self.consume("SEMICOLON")
            return Assignment(name, expr)
        elif self.match("PRINT"):
            self.consume("LPAREN")
            expr = self.parse_expression()
            self.consume("RPAREN")
            self.consume("SEMICOLON")
            return Print(expr)
        else:
            raise Exception("دستور ناشناخته")

    def parse_expression(self):
        node = self.parse_term()
        while self.current()["type"] in ("PLUS", "MINUS"):
            op = self.current()["value"]
            self.pos += 1
            right = self.parse_term()
            node = BinaryOp(node, op, right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.current()["type"] in ("MULT", "DIV"):
            op = self.current()["value"]
            self.pos += 1
            right = self.parse_factor()
            node = BinaryOp(node, op, right)
        return node

    def parse_factor(self):
        tok = self.current()
        if self.match("NUMBER"):
            return Number(tok["value"])
        elif self.match("IDENT"):
            return Identifier(tok["value"])
        elif self.match("LPAREN"):
            expr = self.parse_expression()
            self.consume("RPAREN")
            return expr
        else:
            raise Exception("انتظار عدد یا متغیر داشتیم")