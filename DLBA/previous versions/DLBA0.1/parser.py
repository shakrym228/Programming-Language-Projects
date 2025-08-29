from ast_nodes import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, type_):
        token = self.current()
        if token and token.type == type_:
            self.pos += 1
            return token
        else:
            raise Exception(f"انتظار {type_} ولی دریافت شد {token.type if token else 'EOF'}")

    def parse(self):
        statements = []
        while self.current():
            statements.append(self.statement())
        return statements

    def statement(self):
        tok = self.current()
        if tok.type == 'LET':
            self.eat('LET')
            name = self.eat('IDENT').value
            self.eat('ASSIGN')
            expr = self.expr()
            self.eat('SEMICOLON')
            return Assignment(name, expr)
        elif tok.type == 'PRINT':
            self.eat('PRINT')
            expr = self.expr()
            self.eat('SEMICOLON')
            return Print(expr)
        elif tok.type == 'IF':
            return self.if_statement()
        else:
            raise Exception(f"دستور ناشناخته: {tok}")

    def if_statement(self):
        self.eat('IF')
        self.eat('LPAREN')
        condition = self.expr()
        self.eat('RPAREN')
        self.eat('LBRACE')
        then_branch = []
        while self.current().type != 'RBRACE':
            then_branch.append(self.statement())
        self.eat('RBRACE')

        else_branch = []
        if self.current() and self.current().type == 'ELSE':
            self.eat('ELSE')
            self.eat('LBRACE')
            while self.current().type != 'RBRACE':
                else_branch.append(self.statement())
            self.eat('RBRACE')

        return IfStatement(condition, then_branch, else_branch)

    def expr(self):
        node = self.comparison()
        while self.current() and self.current().type in ('PLUS', 'MINUS'):
            op = self.eat(self.current().type).value
            right = self.comparison()
            node = BinaryOp(node, op, right)
        return node

    def comparison(self):
        node = self.term()
        while self.current() and self.current().type in ('LT','GT','LE','GE','EQ','NE'):
            op_token = self.eat(self.current().type)
            right = self.term()
            node = BinaryOp(node, op_token.value, right)
        return node

    def term(self):
        node = self.factor()
        while self.current() and self.current().type in ('STAR', 'SLASH'):
            op = self.eat(self.current().type).value
            right = self.factor()
            node = BinaryOp(node, op, right)
        return node

    def factor(self):
        return self.atom()

    def atom(self):
        tok = self.current()
        if tok.type == 'NUMBER':
            self.eat('NUMBER')
            return Number(tok.value)
        elif tok.type == 'IDENT':
            self.eat('IDENT')
            return Identifier(tok.value)
        elif tok.type == 'LPAREN':
            self.eat('LPAREN')
            expr = self.expr()
            self.eat('RPAREN')
            return expr
        else:
            raise Exception(f"انتظار عدد یا متغیر یا پرانتز، اما دریافت شد: {tok.type}")