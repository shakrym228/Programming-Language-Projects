# parser.py
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

        # let declaration
        if tok.type == 'LET':
            self.eat('LET')
            name_tok = self.eat('IDENT')
            self.eat('ASSIGN')
            expr = self.expr()
            if self.peek() and self.peek().type == 'SEMICOLON':
                self.eat('SEMICOLON')
            return Assign(name_tok.value, expr, declare=True)

        # function definition
        if tok.type == 'FUNC':
            self.eat('FUNC')
            name = self.eat('IDENT').value
            self.eat('LPAREN')
            params = []
            if self.peek() and self.peek().type == 'IDENT':
                params.append(self.eat('IDENT').value)
                while self.peek() and self.peek().type == 'COMMA':
                    self.eat('COMMA')
                    params.append(self.eat('IDENT').value)
            self.eat('RPAREN')
            self.eat('LBRACE')
            body = []
            while self.peek() and self.peek().type != 'RBRACE':
                body.append(self.statement())
            self.eat('RBRACE')
            return FunctionDef(name, params, body)

        # assignment (reassignment without let)
        if tok.type == 'IDENT' and self.peek_next() and self.peek_next().type == 'ASSIGN':
            name_tok = self.eat('IDENT')
            self.eat('ASSIGN')
            expr = self.expr()
            if self.peek() and self.peek().type == 'SEMICOLON':
                self.eat('SEMICOLON')
            return Assign(name_tok.value, expr, declare=False)

        # print
        if tok.type == 'PRINT':
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

        # return
        if tok.type == 'RETURN':
            self.eat('RETURN')
            if self.peek() and self.peek().type != 'SEMICOLON':
                expr = self.expr()
            else:
                expr = None
            if self.peek() and self.peek().type == 'SEMICOLON':
                self.eat('SEMICOLON')
            return Return(expr)

        # if / while
        if tok.type == 'IF':
            return self.if_statement()
        if tok.type == 'WHILE':
            return self.while_statement()

        # --- NEW: function-call (expression) as a standalone statement ---
        # If we see IDENT followed by LPAREN, it's a call expression used as a statement:
        if tok.type == 'IDENT' and self.peek_next() and self.peek_next().type == 'LPAREN':
            expr = self.expr()   # primary() will build Call node
            # optional semicolon
            if self.peek() and self.peek().type == 'SEMICOLON':
                self.eat('SEMICOLON')
            return expr  # Call node will be executed by interpreter

        # If none matched, it's an error
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

        elif_branches = []
        while self.peek() and self.peek().type == 'ELIF':
            self.eat('ELIF')
            self.eat('LPAREN')
            econd = self.expr()
            self.eat('RPAREN')
            self.eat('LBRACE')
            ebranch = []
            while self.peek() and self.peek().type != 'RBRACE':
                ebranch.append(self.statement())
            self.eat('RBRACE')
            elif_branches.append((econd, ebranch))

        else_branch = None
        if self.peek() and self.peek().type == 'ELSE':
            self.eat('ELSE')
            self.eat('LBRACE')
            else_branch = []
            while self.peek() and self.peek().type != 'RBRACE':
                else_branch.append(self.statement())
            self.eat('RBRACE')

        return If(condition, then_branch, elif_branches, else_branch)

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

    # Expression precedence (logical / equality / comparison / additive / multiplicative / unary / primary)
    def expr(self):
        return self.or_expr()

    def or_expr(self):
        node = self.and_expr()
        while self.peek() and self.peek().type == 'OP' and self.peek().value in ('||',):
            op = self.eat('OP').value
            right = self.and_expr()
            node = BinOp(node, op, right)
        return node

    def and_expr(self):
        node = self.equality()
        while self.peek() and self.peek().type == 'OP' and self.peek().value in ('&&',):
            op = self.eat('OP').value
            right = self.equality()
            node = BinOp(node, op, right)
        return node

    def equality(self):
        node = self.comparison()
        while self.peek() and self.peek().type == 'OP' and self.peek().value in ('==','!='):
            op = self.eat('OP').value
            right = self.comparison()
            node = BinOp(node, op, right)
        return node

    def comparison(self):
        node = self.additive()
        while self.peek() and self.peek().type == 'OP' and self.peek().value in ('<','>','<=','>='):
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
        while self.peek() and self.peek().type == 'OP' and self.peek().value in ('*','/','%'):
            op = self.eat('OP').value
            right = self.factor()
            node = BinOp(node, op, right)
        return node

    def factor(self):
        tok = self.peek()
        if tok and tok.type == 'OP' and tok.value in ('!','-'):
            op = self.eat('OP').value
            operand = self.factor()
            return UnaryOp(op, operand)
        return self.primary()

    def primary(self):
        tok = self.peek()
        if not tok:
            raise Exception("Unexpected end of input in primary")
        if tok.type == 'NUMBER':
            val = self.eat('NUMBER').value
            return Number(val)
        if tok.type == 'STRING':
            val = self.eat('STRING').value
            return String(val)
        if tok.type == 'TRUE':
            self.eat('TRUE')
            return Boolean(True)
        if tok.type == 'FALSE':
            self.eat('FALSE')
            return Boolean(False)
        if tok.type == 'IDENT':
            # could be a function call or variable
            name = self.eat('IDENT').value
            if self.peek() and self.peek().type == 'LPAREN':
                # call
                self.eat('LPAREN')
                args = []
                if self.peek() and self.peek().type != 'RPAREN':
                    args.append(self.expr())
                    while self.peek() and self.peek().type == 'COMMA':
                        self.eat('COMMA')
                        args.append(self.expr())
                self.eat('RPAREN')
                return Call(Var(name), args)
            return Var(name)
        if tok.type == 'LPAREN':
            self.eat('LPAREN')
            node = self.expr()
            self.eat('RPAREN')
            return node
        raise Exception(f"Unexpected token in expression: {tok.type}")
