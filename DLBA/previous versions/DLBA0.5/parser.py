# parser.py - attaches lineno & filename to nodes where possible
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
            raise Exception(f"Expected {expected_type} but got {tok.type} at {tok.filename}:{tok.lineno}")
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
        # import
        if tok.type == 'IMPORT':
            imp_tok = self.eat('IMPORT')
            path_tok = self.eat('STRING')
            node = Import(path_tok.value)
            node.lineno = path_tok.lineno
            node.filename = path_tok.filename
            if self.peek() and self.peek().type == 'SEMICOLON':
                self.eat('SEMICOLON')
            return node
        # let
        if tok.type == 'LET':
            let_tok = self.eat('LET')
            name_tok = self.eat('IDENT')
            self.eat('ASSIGN')
            expr = self.expr()
            node = Assign(name_tok.value, expr, declare=True)
            node.lineno = getattr(expr, 'lineno', let_tok.lineno)
            node.filename = getattr(expr, 'filename', let_tok.filename)
            if self.peek() and self.peek().type == 'SEMICOLON':
                self.eat('SEMICOLON')
            return node
        # func
        if tok.type == 'FUNC':
            func_tok = self.eat('FUNC')
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
            node = FunctionDef(name, params, body)
            node.lineno = func_tok.lineno
            node.filename = func_tok.filename
            return node
        # assignment without let
        if tok.type == 'IDENT' and self.peek_next() and self.peek_next().type == 'ASSIGN':
            name_tok = self.eat('IDENT')
            self.eat('ASSIGN')
            expr = self.expr()
            node = Assign(name_tok.value, expr, declare=False)
            node.lineno = getattr(expr, 'lineno', name_tok.lineno)
            node.filename = getattr(expr, 'filename', name_tok.filename)
            if self.peek() and self.peek().type == 'SEMICOLON':
                self.eat('SEMICOLON')
            return node
        # print
        if tok.type == 'PRINT':
            p_tok = self.eat('PRINT')
            if self.peek() and self.peek().type == 'LPAREN':
                self.eat('LPAREN')
                expr = self.expr()
                self.eat('RPAREN')
            else:
                expr = self.expr()
            node = Print(expr)
            node.lineno = getattr(expr, 'lineno', p_tok.lineno)
            node.filename = getattr(expr, 'filename', p_tok.filename)
            if self.peek() and self.peek().type == 'SEMICOLON':
                self.eat('SEMICOLON')
            return node
        # return
        if tok.type == 'RETURN':
            r_tok = self.eat('RETURN')
            expr = None
            if self.peek() and self.peek().type != 'SEMICOLON':
                expr = self.expr()
            node = Return(expr)
            node.lineno = getattr(expr, 'lineno', r_tok.lineno)
            node.filename = getattr(expr, 'filename', r_tok.filename)
            if self.peek() and self.peek().type == 'SEMICOLON':
                self.eat('SEMICOLON')
            return node
        # if / while
        if tok.type == 'IF':
            return self.if_statement()
        if tok.type == 'WHILE':
            return self.while_statement()
        # function call as statement: IDENT LPAREN
        if tok.type == 'IDENT' and self.peek_next() and self.peek_next().type == 'LPAREN':
            expr = self.expr()
            if self.peek() and self.peek().type == 'SEMICOLON':
                self.eat('SEMICOLON')
            # expr will be a Call node; ensure lineno/filename set if possible
            return expr
        raise Exception(f"Unknown statement start: {tok.type} at {tok.filename}:{tok.lineno}")

    def if_statement(self):
        if_tok = self.eat('IF')
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

        node = If(condition, then_branch, elif_branches, else_branch)
        node.lineno = getattr(condition, 'lineno', if_tok.lineno)
        node.filename = getattr(condition, 'filename', if_tok.filename)
        return node

    def while_statement(self):
        w_tok = self.eat('WHILE')
        self.eat('LPAREN')
        condition = self.expr()
        self.eat('RPAREN')
        self.eat('LBRACE')
        body = []
        while self.peek() and self.peek().type != 'RBRACE':
            body.append(self.statement())
        self.eat('RBRACE')
        node = While(condition, body)
        node.lineno = getattr(condition, 'lineno', w_tok.lineno)
        node.filename = getattr(condition, 'filename', w_tok.filename)
        return node

    # expression precedence
    def expr(self):
        return self.or_expr()

    def or_expr(self):
        node = self.and_expr()
        while self.peek() and self.peek().type == 'OP' and self.peek().value in ('||',):
            op_tok = self.eat('OP')
            right = self.and_expr()
            node = BinOp(node, op_tok.value, right)
            node.lineno = op_tok.lineno; node.filename = op_tok.filename
        return node

    def and_expr(self):
        node = self.equality()
        while self.peek() and self.peek().type == 'OP' and self.peek().value in ('&&',):
            op_tok = self.eat('OP')
            right = self.equality()
            node = BinOp(node, op_tok.value, right)
            node.lineno = op_tok.lineno; node.filename = op_tok.filename
        return node

    def equality(self):
        node = self.comparison()
        while self.peek() and self.peek().type == 'OP' and self.peek().value in ('==','!='):
            op_tok = self.eat('OP')
            right = self.comparison()
            node = BinOp(node, op_tok.value, right)
            node.lineno = op_tok.lineno; node.filename = op_tok.filename
        return node

    def comparison(self):
        node = self.additive()
        while self.peek() and self.peek().type == 'OP' and self.peek().value in ('<','>','<=','>='):
            op_tok = self.eat('OP')
            right = self.additive()
            node = BinOp(node, op_tok.value, right)
            node.lineno = op_tok.lineno; node.filename = op_tok.filename
        return node

    def additive(self):
        node = self.term()
        while self.peek() and self.peek().type == 'OP' and self.peek().value in ('+','-'):
            op_tok = self.eat('OP')
            right = self.term()
            node = BinOp(node, op_tok.value, right)
            node.lineno = op_tok.lineno; node.filename = op_tok.filename
        return node

    def term(self):
        node = self.factor()
        while self.peek() and self.peek().type == 'OP' and self.peek().value in ('*','/','%'):
            op_tok = self.eat('OP')
            right = self.factor()
            node = BinOp(node, op_tok.value, right)
            node.lineno = op_tok.lineno; node.filename = op_tok.filename
        return node

    def factor(self):
        tok = self.peek()
        if tok and tok.type == 'OP' and tok.value in ('!','-'):
            op_tok = self.eat('OP')
            operand = self.factor()
            node = UnaryOp(op_tok.value, operand)
            node.lineno = op_tok.lineno; node.filename = op_tok.filename
            return node
        return self.primary()

    def primary(self):
        tok = self.peek()
        if not tok:
            raise Exception("Unexpected end of input in primary")
        if tok.type == 'NUMBER':
            t = self.eat('NUMBER')
            node = Number(t.value)
            node.lineno = t.lineno; node.filename = t.filename
            return node
        if tok.type == 'STRING':
            t = self.eat('STRING')
            node = String(t.value)
            node.lineno = t.lineno; node.filename = t.filename
            return node
        if tok.type == 'TRUE':
            t = self.eat('TRUE')
            node = Boolean(True)
            node.lineno = t.lineno; node.filename = t.filename
            return node
        if tok.type == 'FALSE':
            t = self.eat('FALSE')
            node = Boolean(False)
            node.lineno = t.lineno; node.filename = t.filename
            return node
        if tok.type == 'IDENT':
            name_tok = self.eat('IDENT')
            # call?
            if self.peek() and self.peek().type == 'LPAREN':
                self.eat('LPAREN')
                args = []
                if self.peek() and self.peek().type != 'RPAREN':
                    args.append(self.expr())
                    while self.peek() and self.peek().type == 'COMMA':
                        self.eat('COMMA')
                        args.append(self.expr())
                rp = self.eat('RPAREN')
                node = Call(Var(name_tok.value), args)
                node.lineno = name_tok.lineno; node.filename = name_tok.filename
                return node
            node = Var(name_tok.value)
            node.lineno = name_tok.lineno; node.filename = name_tok.filename
            return node
        if tok.type == 'LPAREN':
            lp = self.eat('LPAREN')
            node = self.expr()
            rp = self.eat('RPAREN')
            # preserve lineno/filename if missing
            node.lineno = getattr(node, 'lineno', lp.lineno)
            node.filename = getattr(node, 'filename', lp.filename)
            return node
        raise Exception(f"Unexpected token in expression: {tok.type} at {tok.filename}:{tok.lineno}")
