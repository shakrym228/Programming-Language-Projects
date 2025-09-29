# parser.py - DLBA parser (v0.8)
from ast_nodes import *


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def peek_next(self):
        return self.tokens[self.pos + 1] if (self.pos + 1) < len(self.tokens) else None

    def eat(self, expected_type=None):
        tok = self.peek()
        if not tok:
            raise Exception("Unexpected end of input")
        if expected_type and tok.type != expected_type:
            raise Exception(
                f"Expected {expected_type} but got {tok.type} at {tok.filename}:{tok.lineno}:{tok.col}"
            )
        self.pos += 1
        return tok

    def _skip_newlines(self):
        while self.peek() and self.peek().type == "NEWLINE":
            self.eat("NEWLINE")

    def _consume_terminator_or_validate(self):
        nxt = self.peek()
        if nxt and nxt.type == "SEMICOLON":
            self.eat("SEMICOLON")
        elif nxt and nxt.type == "NEWLINE":
            self.eat("NEWLINE")
        elif nxt and nxt.type == "RBRACE":
            pass
        elif nxt is None:
            pass
        else:
            raise Exception(
                f"Expected ';' or newline after statement but got {nxt.type} at {nxt.filename}:{nxt.lineno}:{nxt.col}"
            )

    def _parse_block_statements(self):
        stmts = []
        while self.peek() and self.peek().type != "RBRACE":
            self._skip_newlines()
            if not self.peek() or self.peek().type == "RBRACE":
                break
            stmt = self.statement()
            self._consume_terminator_or_validate()
            stmts.append(stmt)
        return stmts

    def parse(self):
        statements = []
        while self.peek():
            self._skip_newlines()
            if not self.peek():
                break
            stmt = self.statement()
            self._consume_terminator_or_validate()
            statements.append(stmt)
        return statements

    # statement parsing (same as v0.7) ...
    # (omitted here for brevity — use the full statement implementation from v0.7)
    # Important: keep support for FROM / IMPORT / LET / FUNC / ASSIGN / PRINT / RETURN / IF / WHILE / expr-stmt

    # For brevity paste the full statement() implementation from your current v0.7 parser here.
    # Ensure when constructing Number/String/Var nodes you set node.col = token.col (as in earlier steps).
    def statement(self):
        tok = self.peek()
        if not tok:
            raise Exception("Unexpected end of input in statement")

        # from "path" import name1, name2
        if tok.type == "FROM":
            self.eat("FROM")
            path_tok = self.eat("STRING")
            self.eat("IMPORT")
            names = []
            names.append(self.eat("IDENT").value)
            while self.peek() and self.peek().type == "COMMA":
                self.eat("COMMA")
                names.append(self.eat("IDENT").value)
            node = Import(path_tok.value, as_name=None, names=names)
            node.lineno = path_tok.lineno
            node.filename = path_tok.filename
            return node

        # import "path" [as alias]
        if tok.type == "IMPORT":
            imp_tok = self.eat("IMPORT")
            path_tok = self.eat("STRING")
            as_name = None
            if self.peek() and self.peek().type == "AS":
                self.eat("AS")
                name_tok = self.eat("IDENT")
                as_name = name_tok.value
            node = Import(path_tok.value, as_name=as_name, names=None)
            node.lineno = path_tok.lineno
            node.filename = path_tok.filename
            return node

        # let decl
        if tok.type == "LET":
            let_tok = self.eat("LET")
            name_tok = self.eat("IDENT")
            self.eat("ASSIGN")
            expr = self.expr()
            node = Assign(name_tok.value, expr, declare=True)
            node.lineno = getattr(expr, "lineno", let_tok.lineno)
            node.filename = getattr(expr, "filename", let_tok.filename)
            return node

        # func def
        if tok.type == "FUNC":
            func_tok = self.eat("FUNC")
            name = self.eat("IDENT").value
            self.eat("LPAREN")
            params = []
            if self.peek() and self.peek().type == "IDENT":
                params.append(self.eat("IDENT").value)
                while self.peek() and self.peek().type == "COMMA":
                    self.eat("COMMA")
                    params.append(self.eat("IDENT").value)
            self.eat("RPAREN")
            self.eat("LBRACE")
            body = self._parse_block_statements()
            self.eat("RBRACE")
            node = FunctionDef(name, params, body)
            node.lineno = func_tok.lineno
            node.filename = func_tok.filename
            return node

        # assignment without let
        if (
            tok.type == "IDENT"
            and self.peek_next()
            and self.peek_next().type == "ASSIGN"
        ):
            name_tok = self.eat("IDENT")
            self.eat("ASSIGN")
            expr = self.expr()
            node = Assign(name_tok.value, expr, declare=False)
            node.lineno = getattr(expr, "lineno", name_tok.lineno)
            node.filename = getattr(expr, "filename", name_tok.filename)
            return node

        # print
        if tok.type == "PRINT":
            p_tok = self.eat("PRINT")
            if self.peek() and self.peek().type == "LPAREN":
                self.eat("LPAREN")
                expr = self.expr()
                self.eat("RPAREN")
            else:
                expr = self.expr()
            node = Print(expr)
            node.lineno = getattr(expr, "lineno", p_tok.lineno)
            node.filename = getattr(expr, "filename", p_tok.filename)
            return node

        # return
        if tok.type == "RETURN":
            r_tok = self.eat("RETURN")
            expr = None
            if self.peek() and self.peek().type not in (
                "SEMICOLON",
                "NEWLINE",
                "RBRACE",
            ):
                expr = self.expr()
            node = Return(expr)
            node.lineno = (
                getattr(expr, "lineno", r_tok.lineno) if expr else r_tok.lineno
            )
            node.filename = (
                getattr(expr, "filename", r_tok.filename) if expr else r_tok.filename
            )
            return node

        # if / while
        if tok.type == "IF":
            return self.if_statement()
        if tok.type == "WHILE":
            return self.while_statement()

        # expression as statement
        if tok.type in ("IDENT", "STRING", "NUMBER", "LPAREN", "LBRACK"):
            expr = self.expr()
            return expr

        raise Exception(
            f"Unknown statement start: {tok.type} at {tok.filename}:{tok.lineno}"
        )

    def if_statement(self):
        if_tok = self.eat("IF")
        self.eat("LPAREN")
        condition = self.expr()
        self.eat("RPAREN")
        self.eat("LBRACE")
        then_branch = self._parse_block_statements()
        self.eat("RBRACE")

        elif_branches = []
        while self.peek() and self.peek().type == "ELIF":
            self.eat("ELIF")
            self.eat("LPAREN")
            econd = self.expr()
            self.eat("RPAREN")
            self.eat("LBRACE")
            ebranch = self._parse_block_statements()
            self.eat("RBRACE")
            elif_branches.append((econd, ebranch))

        else_branch = None
        if self.peek() and self.peek().type == "ELSE":
            self.eat("ELSE")
            self.eat("LBRACE")
            else_branch = self._parse_block_statements()
            self.eat("RBRACE")

        node = If(condition, then_branch, elif_branches, else_branch)
        node.lineno = getattr(condition, "lineno", if_tok.lineno)
        node.filename = getattr(condition, "filename", if_tok.filename)
        return node

    def while_statement(self):
        w_tok = self.eat("WHILE")
        self.eat("LPAREN")
        condition = self.expr()
        self.eat("RPAREN")
        self.eat("LBRACE")
        body = self._parse_block_statements()
        self.eat("RBRACE")
        node = While(condition, body)
        node.lineno = getattr(condition, "lineno", w_tok.lineno)
        node.filename = getattr(condition, "filename", w_tok.filename)
        return node

    # --- Expressions ---
    def expr(self):
        return self.or_expr()

    def or_expr(self):
        node = self.and_expr()
        while self.peek() and self.peek().type == "OP" and self.peek().value in ("||",):
            op_tok = self.eat("OP")
            right = self.and_expr()
            node = BinOp(node, op_tok.value, right)
            node.lineno = op_tok.lineno
            node.filename = op_tok.filename
            node.col = op_tok.col
        return node

    def and_expr(self):
        node = self.equality()
        while self.peek() and self.peek().type == "OP" and self.peek().value in ("&&",):
            op_tok = self.eat("OP")
            right = self.equality()
            node = BinOp(node, op_tok.value, right)
            node.lineno = op_tok.lineno
            node.filename = op_tok.filename
            node.col = op_tok.col
        return node

    def equality(self):
        node = self.comparison()
        while (
            self.peek()
            and self.peek().type == "OP"
            and self.peek().value in ("==", "!=")
        ):
            op_tok = self.eat("OP")
            right = self.comparison()
            node = BinOp(node, op_tok.value, right)
            node.lineno = op_tok.lineno
            node.filename = op_tok.filename
            node.col = op_tok.col
        return node

    def comparison(self):
        node = self.additive()
        while (
            self.peek()
            and self.peek().type == "OP"
            and self.peek().value in ("<", ">", "<=", ">=")
        ):
            op_tok = self.eat("OP")
            right = self.additive()
            node = BinOp(node, op_tok.value, right)
            node.lineno = op_tok.lineno
            node.filename = op_tok.filename
            node.col = op_tok.col
        return node

    def additive(self):
        node = self.term()
        while (
            self.peek() and self.peek().type == "OP" and self.peek().value in ("+", "-")
        ):
            op_tok = self.eat("OP")
            right = self.term()
            node = BinOp(node, op_tok.value, right)
            node.lineno = op_tok.lineno
            node.filename = op_tok.filename
            node.col = op_tok.col
        return node

    def term(self):
        node = self.factor()
        while (
            self.peek()
            and self.peek().type == "OP"
            and self.peek().value in ("*", "/", "%")
        ):
            op_tok = self.eat("OP")
            right = self.factor()
            node = BinOp(node, op_tok.value, right)
            node.lineno = op_tok.lineno
            node.filename = op_tok.filename
            node.col = op_tok.col
        return node

    def factor(self):
        tok = self.peek()
        if tok and tok.type == "OP" and tok.value in ("!", "-"):
            op_tok = self.eat("OP")
            operand = self.factor()
            node = UnaryOp(op_tok.value, operand)
            node.lineno = op_tok.lineno
            node.filename = op_tok.filename
            node.col = op_tok.col
            return node
        return self.postfix()

    def postfix(self):
        node = self.primary()
        while True:
            nxt = self.peek()
            if not nxt:
                break
            if nxt.type == "LPAREN":
                self.eat("LPAREN")
                args = []
                if self.peek() and self.peek().type != "RPAREN":
                    args.append(self.expr())
                    while self.peek() and self.peek().type == "COMMA":
                        self.eat("COMMA")
                        args.append(self.expr())
                rp = self.eat("RPAREN")
                node = Call(node, args)
                node.lineno = getattr(node, "lineno", rp.lineno)
                node.filename = getattr(node, "filename", rp.filename)
                node.col = getattr(node, "col", rp.col)
                continue
            if nxt.type == "DOT":
                self.eat("DOT")
                mem = self.eat("IDENT")
                node = ModuleAccess(node, mem.value)
                node.lineno = mem.lineno
                node.filename = mem.filename
                node.col = mem.col
                continue
            if nxt.type == "LBRACK":
                # index or slice
                self.eat("LBRACK")
                # check if slice (start:stop) or single index/expression
                if self.peek() and self.peek().type != "RBRACK":
                    # parse start expr (may be empty)
                    start_expr = None
                    if self.peek() and self.peek().type != "COLON":
                        start_expr = self.expr()
                    if self.peek() and self.peek().type == "COLON":
                        # it's a slice
                        self.eat("COLON")
                        stop_expr = None
                        if self.peek() and self.peek().type != "RBRACK":
                            stop_expr = self.expr()
                        slice_node = Slice(start_expr, stop_expr)
                        self.eat("RBRACK")
                        node = Index(node, slice_node)
                        continue
                    else:
                        # single index
                        idx = start_expr
                        self.eat("RBRACK")
                        node = Index(node, idx)
                        continue
                else:
                    # empty brackets -> invalid generally
                    self.eat("RBRACK")
                    raise Exception(
                        f"Empty index [] not allowed at {nxt.filename}:{nxt.lineno}:{nxt.col}"
                    )
            break
        return node

    def primary(self):
        tok = self.peek()
        if not tok:
            raise Exception("Unexpected end of input in primary")
        if tok.type == "NUMBER":
            t = self.eat("NUMBER")
            node = Number(t.value)
            node.lineno = t.lineno
            node.filename = t.filename
            node.col = t.col
            return node
        if tok.type == "STRING":
            t = self.eat("STRING")
            node = String(t.value)
            node.lineno = t.lineno
            node.filename = t.filename
            node.col = t.col
            return node
        if tok.type == "TRUE":
            t = self.eat("TRUE")
            node = Boolean(True)
            node.lineno = t.lineno
            node.filename = t.filename
            node.col = t.col
            return node
        if tok.type == "FALSE":
            t = self.eat("FALSE")
            node = Boolean(False)
            node.lineno = t.lineno
            node.filename = t.filename
            node.col = t.col
            return node
        if tok.type == "IDENT":
            t = self.eat("IDENT")
            node = Var(t.value)
            node.lineno = t.lineno
            node.filename = t.filename
            node.col = t.col
            return node
        if tok.type == "LBRACK":
            lb = self.eat("LBRACK")
            elems = []
            if self.peek() and self.peek().type != "RBRACK":
                elems.append(self.expr())
                while self.peek() and self.peek().type == "COMMA":
                    self.eat("COMMA")
                    elems.append(self.expr())
            self.eat("RBRACK")
            node = ListLiteral(elems)
            node.lineno = lb.lineno
            node.filename = lb.filename
            node.col = lb.col
            return node
        if tok.type == "LBRACE":
            lb = self.eat("LBRACE")
            pairs = []
            if self.peek() and self.peek().type != "RBRACE":
                while True:
                    if self.peek().type == "STRING":
                        k_tok = self.eat("STRING")
                        key_node = String(k_tok.value)
                        key_node.lineno = k_tok.lineno
                        key_node.filename = k_tok.filename
                        key_node.col = k_tok.col
                    elif self.peek().type == "IDENT":
                        k_tok = self.eat("IDENT")
                        key_node = String(k_tok.value)
                        key_node.lineno = k_tok.lineno
                        key_node.filename = k_tok.filename
                        key_node.col = k_tok.col
                    else:
                        raise Exception(
                            f"Expected STRING or IDENT as dict key but got {self.peek().type} at {self.peek().filename}:{self.peek().lineno}:{self.peek().col}"
                        )
                    self.eat("COLON")
                    val = self.expr()
                    pairs.append((key_node, val))
                    if self.peek() and self.peek().type == "COMMA":
                        self.eat("COMMA")
                        continue
                    break
            self.eat("RBRACE")
            node = DictLiteral(pairs)
            node.lineno = lb.lineno
            node.filename = lb.filename
            node.col = lb.col
            return node
        if tok.type == "LPAREN":
            lp = self.eat("LPAREN")
            node = self.expr()
            self.eat("RPAREN")
            node.lineno = getattr(node, "lineno", lp.lineno)
            node.filename = getattr(node, "filename", lp.filename)
            node.col = getattr(node, "col", lp.col)
            return node
        raise Exception(
            f"Unexpected token in expression: {tok.type} at {tok.filename}:{tok.lineno}:{tok.col}"
        )
