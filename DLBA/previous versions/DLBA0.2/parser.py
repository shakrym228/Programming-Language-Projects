from ast_nodes import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def peek_next(self):
        return self.tokens[self.pos+1] if (self.pos+1) < len(self.tokens) else None

    def eat(self, expected_type=None):
        tok = self.peek()
        if not tok:
            raise Exception("Unexpected end of input")
        if expected_type and tok.type != expected_type:
            raise Exception(f"Expected {expected_type} but got {tok.type}")
        self.pos += 1
        return tok

    def parse(self):
        stmts = []
        while self.peek():
            stmts.append(self.statement())
        return stmts

    def statement(self):
        tok = self.peek()
        if not tok:
            raise Exception("Unexpected end of input in statement")
        if tok.type == 'LET':
            # let declaration
            self.eat('LET')
            name_tok = self.eat('IDENT')
            self.eat('ASSIGN')
            expr = self.expr()
            if self.peek() and self.peek().type == 'SEMICOLON':
                self.eat('SEMICOLON')
            return Assign(name_tok.value, expr, declare=True)

        elif tok.type == 'IDENT' and self.peek_next() and self.peek_next().type == 'ASSIGN':
            # plain assignment (must exist previously or interpreter will report)
            name_tok = self.eat('IDENT')
            self.eat('ASSIGN')
            expr = self.expr()
            if self.peek() and self.peek().type == 'SEMICOLON':
                self.eat('SEMICOLON')
            return Assign(name_tok.value, expr, declare=False)

        elif tok.type == 'PRINT':
            # print (expr)  or print expr
            self.eat('PRINT')
            if self.peek() and self.peek().type == 'LPAREN':
                self.eat('LPAREN')
                expr = self.expr()
                self.eat('RPAREN')
            else:
                expr = self.expr()
            if self.peek() and self.peek().type == 'SEMICOLON':
                self.eat('SEMICOLON')
            return Print(expr)

        elif tok.type == 'IF':
            return self.if_statement()

        elif tok.type == 'WHILE':
            return self.while_statement()

        else:
            raise Exception(f"Unknown statement start: {tok.type}")

    def if_statement(self):
        self.eat('IF')
        self.eat('LPAREN')
        condition = self.expr()
        self.eat('RPAREN')
        self.eat('LBRACE')
        then_branch = []
        while self.peek() and self.peek().type != 'RBRACE':
            then_branch.append(self.statement())
        self.eat('RBRACE')

        else_branch = None
        if self.peek() and self.peek().type == 'ELSE':
            self.eat('ELSE')
            self.eat('LBRACE')
            else_branch = []
            while self.peek() and self.peek().type != 'RBRACE':
                else_branch.append(self.statement())
            self.eat('RBRACE')
        return If(condition, then_branch, else_branch)

    def while_statement(self):
        self.eat('WHILE')
        self.eat('LPAREN')
        condition = self.expr()
        self.eat('RPAREN')
        self.eat('LBRACE')
        body = []
        while self.peek() and self.peek().type != 'RBRACE':
            body.append(self.statement())
        self.eat('RBRACE')
        return While(condition, body)

    # precedence:
    # expr := comparison
    # comparison := additive ( ( '==' | '!=' | '<' | '>' | '<=' | '>=' ) additive )*
    # additive := term ( ('+'|'-') term )*
    # term := factor (('*'|'/') factor)*
    # factor := NUMBER | TRUE | FALSE | IDENT | ( expr )
    def expr(self):
        return self.comparison()

    def comparison(self):
        node = self.additive()
        while self.peek() and self.peek().type == 'OP' and self.peek().value in ('==','!=','<','>','<=','>='):
            op = self.eat('OP').value
            right = self.additive()
            node = BinOp(node, op, right)
        return node

    def additive(self):
        node = self.term()
        while self.peek() and self.peek().type == 'OP' and self.peek().value in ('+','-'):
            op = self.eat('OP').value
            right = self.term()
            node = BinOp(node, op, right)
        return node

    def term(self):
        node = self.factor()
        while self.peek() and self.peek().type == 'OP' and self.peek().value in ('*','/'):
            op = self.eat('OP').value
            right = self.factor()
            node = BinOp(node, op, right)
        return node

    def factor(self):
        tok = self.peek()
        if not tok:
            raise Exception("Unexpected end of input in factor")
        if tok.type == 'NUMBER':
            return Number(self.eat('NUMBER').value)
        elif tok.type == 'TRUE':
            self.eat('TRUE')
            return Boolean(True)
        elif tok.type == 'FALSE':
            self.eat('FALSE')
            return Boolean(False)
        elif tok.type == 'IDENT':
            return Var(self.eat('IDENT').value)
        elif tok.type == 'LPAREN':
            self.eat('LPAREN')
            node = self.expr()
            self.eat('RPAREN')
            return node
        else:
            raise Exception(f"Unexpected token in expression: {tok.type}")
