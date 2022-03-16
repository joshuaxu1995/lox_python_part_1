from telnetlib import DO
from tokenize import Token
import tokens as ts
from typing import List, Optional
import expr
import stmt
import main_scanner


class Parser:
    class ParseError(Exception):
        pass

    def __init__(self, tokens: List[ts.Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> List[stmt.Stmt]:
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return statements

    def declaration(self) -> Optional[stmt.Stmt]:
        try:
            if self.match(ts.TokenType.CLASS):
                return self.class_declaration()
            elif self.match(ts.TokenType.FUN):
                return self.function_declaration("function")
            elif self.match(ts.TokenType.VAR):
                return self.var_declaration()
            else:
                return self.statement()
        except self.ParseError as e:
            self.synchronize()
            return None

    def class_declaration(self) -> stmt.Stmt:
        name = self.consume(ts.TokenType.IDENTIFIER, "Expect class name.")

        superclass = None
        if self.match(ts.TokenType.LESS):
            self.consume(ts.TokenType.IDENTIFIER, "Expect superclass name.")
            superclass = expr.Variable(self.previous())

        self.consume(ts.TokenType.LEFT_BRACE, "Expect '{' before class body.")

        methods = []
        while not self.check(ts.TokenType.RIGHT_BRACE) and not self.is_at_end():
            methods.append(self.function_declaration("method"))

        self.consume(ts.TokenType.RIGHT_BRACE, "Expect '}' after class body.")
        return stmt.Class(name, superclass, methods)

    def function_declaration(self, kind: str) -> stmt.Function:
        name = self.consume(ts.TokenType.IDENTIFIER, "Expect {kind} name.")
        self.consume(ts.TokenType.LEFT_PAREN, "Expect '(' after {kind} name.")
        parameters = []
        if not self.check(ts.TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    self.error(self.peek(), "Can't have more than 255 parameters.")
                parameters.append(
                    self.consume(ts.TokenType.IDENTIFIER, "Expect parameter name.")
                )

                if not self.match(ts.TokenType.COMMA):
                    break

        self.consume(ts.TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self.consume(ts.TokenType.LEFT_BRACE, "Expect '{' before {kind} body")
        body = self.block()
        return stmt.Function(name, parameters, body)

    def var_declaration(self) -> stmt.Stmt:
        name = self.consume(ts.TokenType.IDENTIFIER, "Expect variable name.")

        initializer = None
        if self.match(ts.TokenType.EQUAL):
            initializer = self.expression()

        self.consume(ts.TokenType.SEMICOLON, "Expect ';' after variable declaration")
        return stmt.Var(name, initializer)

    def statement(self) -> stmt.Stmt:
        if self.match(ts.TokenType.FOR):
            return self.for_statement()
        if self.match(ts.TokenType.IF):
            return self.if_statement()
        if self.match(ts.TokenType.PRINT):
            return self.print_statement()
        if self.match(ts.TokenType.RETURN):
            return self.return_statement()
        if self.match(ts.TokenType.WHILE):
            return self.while_statement()
        if self.match(ts.TokenType.LEFT_BRACE):
            return stmt.Block(self.block())

        return self.expression_statement()

    def return_statement(self) -> stmt.Stmt:
        keyword = self.previous()
        value = None
        if not self.check(ts.TokenType.SEMICOLON):
            value = self.expression()

        self.consume(ts.TokenType.SEMICOLON, "Expect ';' after return value.")
        return stmt.Return(keyword, value)

    def for_statement(self) -> stmt.Stmt:
        self.consume(ts.TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        initializer = None
        if self.match(ts.TokenType.SEMICOLON):
            initializer = None
        elif self.match(ts.TokenType.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()

        condition = None
        if not self.check(ts.TokenType.SEMICOLON):
            condition = self.expression()

        self.consume(ts.TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment = None
        if not self.check(ts.TokenType.RIGHT_PAREN):
            increment = self.expression()

        self.consume(ts.TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")
        body = self.statement()

        if increment is not None:
            body = stmt.Block([body, stmt.Expression(increment)])

        if condition is None:
            condition = expr.Literal(True)
        body = stmt.While(condition, body)

        if initializer is not None:
            body = stmt.Block([initializer, body])

        return body

    def while_statement(self) -> stmt.Stmt:
        self.consume(ts.TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(ts.TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body = self.statement()

        return stmt.While(condition, body)

    def if_statement(self) -> stmt.Stmt:
        self.consume(ts.TokenType.LEFT_PAREN, "Expect '(' after 'if.")
        condition = self.expression()
        self.consume(ts.TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        thenBranch = self.statement()
        elseBranch = None
        if self.match(ts.TokenType.ELSE):
            elseBranch = self.statement()
        return stmt.If(condition, thenBranch, elseBranch)

    def block(self):
        statements = []

        while not self.check(ts.TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())

        self.consume(ts.TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def print_statement(self) -> stmt.Stmt:
        value = self.expression()
        self.consume(ts.TokenType.SEMICOLON, "Expect ';' after value.")
        return stmt.Print(value)

    def expression_statement(self) -> stmt.Stmt:
        temp_expr = self.expression()
        self.consume(ts.TokenType.SEMICOLON, "Expect ';' after expression.")
        return stmt.Expression(temp_expr)

    def expression(self) -> expr.Expr:
        return self.assignment()

    def assignment(self) -> expr.Expr:
        temp_expr = self.or_expr()

        if self.match(ts.TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(temp_expr, expr.Variable):
                name = temp_expr.name
                return expr.Assign(name, value)

            elif isinstance(temp_expr, expr.Get):
                get_expr = temp_expr
                return expr.Set(get_expr.object, get_expr.name, value)

            self.error(equals, "Invalid assignment target.")
        return temp_expr

    def or_expr(self) -> expr.Expr:
        temp_expr = self.and_expr()

        while self.match(ts.TokenType.OR):
            operator = self.previous()
            right = self.and_expr()
            temp_expr = expr.Logical(temp_expr, operator, right)
        return temp_expr

    def and_expr(self) -> expr.Expr:
        temp_expr = self.equality()

        while self.match(ts.TokenType.AND):
            operator = self.previous()
            right = self.equality()
            temp_expr = expr.Logical(temp_expr, operator, right)
        return temp_expr

    def equality(self) -> expr.Expr:
        temp_expr = self.comparison()
        while self.match(ts.TokenType.BANG_EQUAL, ts.TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            temp_expr = expr.Binary(temp_expr, operator, right)
        return temp_expr

    def match(self, *tokens) -> bool:
        for token_type in tokens:
            if self.check(token_type):
                self.advance()
                return True

        return False

    def check(self, type) -> bool:
        if self.is_at_end():
            return False
        peeked_type = self.peek()
        return peeked_type.type == type

    def advance(self) -> ts.Token:
        if not self.is_at_end():
            self.current = self.current + 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().type == ts.TokenType.EOF

    def peek(self) -> ts.Token:
        return self.tokens[self.current]

    def previous(self) -> ts.Token:
        return self.tokens[self.current - 1]

    def comparison(self) -> expr.Expr:
        temp_expr = self.term()
        while self.match(
            ts.TokenType.GREATER,
            ts.TokenType.GREATER_EQUAL,
            ts.TokenType.LESS,
            ts.TokenType.LESS_EQUAL,
        ):
            operator = self.previous()
            right = self.term()
            temp_expr = expr.Binary(temp_expr, operator, right)
        return temp_expr

    def term(self) -> expr.Expr:
        temp_expr = self.factor()
        while self.match(ts.TokenType.MINUS, ts.TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            temp_expr = expr.Binary(temp_expr, operator, right)
        return temp_expr

    def factor(self) -> expr.Expr:
        temp_expr = self.unary()
        while self.match(ts.TokenType.SLASH, ts.TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            temp_expr = expr.Binary(temp_expr, operator, right)
        return temp_expr

    def unary(self) -> expr.Expr:
        if self.match(ts.TokenType.BANG, ts.TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return expr.Unary(operator, right)
        else:
            return self.call()

    def call(self) -> expr.Expr:
        temp_expr = self.primary()

        while True:
            if self.match(ts.TokenType.LEFT_PAREN):
                temp_expr = self.finish_call(temp_expr)
            elif self.match(ts.TokenType.DOT):
                name = self.consume(
                    ts.TokenType.IDENTIFIER, "Expect property name after '.'."
                )
                temp_expr = expr.Get(temp_expr, name)
            else:
                break
        return temp_expr

    def finish_call(self, callee: expr.Expr) -> expr.Expr:
        arguments = []
        if not self.check(ts.TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    self.error(self.peek(), "Can't have more than 255 arguments.")
                arguments.append(self.expression())
                if not self.match(ts.TokenType.COMMA):
                    break

        paren = self.consume(ts.TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        return expr.Call(callee, paren, arguments)

    def primary(self) -> expr.Expr:
        if self.match(ts.TokenType.FALSE):
            return expr.Literal(False)
        if self.match(ts.TokenType.TRUE):
            return expr.Literal(True)
        if self.match(ts.TokenType.NIL):
            return expr.Literal(None)

        if self.match(ts.TokenType.NUMBER, ts.TokenType.STRING):
            return expr.Literal(self.previous().literal)

        if self.match(ts.TokenType.SUPER):
            keyword = self.previous()
            self.consume(ts.TokenType.DOT, "Expect '.' after 'super'.")
            method = self.consume(
                ts.TokenType.IDENTIFIER, "Expect superclass method name."
            )
            return expr.Super(keyword, method)

        if self.match(ts.TokenType.THIS):
            return expr.This(self.previous())

        if self.match(ts.TokenType.IDENTIFIER):
            return expr.Variable(self.previous())

        if self.match(ts.TokenType.LEFT_PAREN):
            temp_expr = self.expression()
            self.consume(ts.TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return expr.Grouping(temp_expr)

        raise self.error(self.peek(), "Expect expression.")

    def consume(self, type: ts.TokenType, message: str) -> None:
        if self.check(type):
            return self.advance()

        raise self.error(self.peek(), message)

    def error(self, token: ts.Token, message: str):
        main_scanner.error(token, message)
        return Parser.ParseError()

    def synchronize(self) -> None:
        self.advance()
        while not self.is_at_end:
            if self.previous().type == ts.TokenType.SEMICOLON:
                return

            if (
                self.peek().type == ts.TokenType.CLASS
                or self.peek().type == ts.TokenType.FOR
                or self.peek().type == ts.TokenType.FUN
                or self.peek().type == ts.TokenType.IF
                or self.peek().type == ts.TokenType.PRINT
                or self.peek().type == ts.TokenType.RETURN
                or self.peek().type == ts.TokenType.VAR
                or self.peek().type == ts.TokenType.WHILE
            ):
                return

        self.advance()
