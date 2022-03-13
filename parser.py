import tokens as ts
from typing import List, Optional
import expr
import stmt
import main_scanner

class Parser():

    class ParseError(Exception):
        pass

    def __init__(self, tokens: List[ts.Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> List[stmt.Stmt]:
        statements = []
        while (not self.is_at_end()):
            statements.append(self.declaration())
        return statements
    
    def declaration(self) -> Optional[stmt.Stmt]:
        try:
            if (self.match(ts.TokenType.VAR)):
                return self.var_declaration()
            else:
                return self.statement()
        except self.ParseError as e:
            self.synchronize()
            return None
        
    def var_declaration(self) -> stmt.Stmt:
        name = self.consume(ts.TokenType.IDENTIFIER, "Expect variable name.")

        initializer = None
        if (self.match(ts.TokenType.EQUAL)):
            initializer = self.expression()
        
        self.consume(ts.TokenType.SEMICOLON, "Expect ';' after variable declaration")
        return stmt.Var(name, initializer)
    
    def statement(self) -> stmt.Stmt:
        if (self.match(ts.TokenType.PRINT)):
            return self.print_statement()
        if (self.match(ts.TokenType.LEFT_BRACE)):
            return stmt.Block(self.block())
        
        return self.expression_statement()
    
    def block(self):
        statements = []

        while (not self.check(ts.TokenType.RIGHT_BRACE) and not self.is_at_end()):
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
        temp_expr = self.equality()

        if (self.match(ts.TokenType.EQUAL)):
            equals = self.previous()
            value = self.assignment()

            if isinstance(temp_expr, expr.Variable):
                name = temp_expr.name
                return expr.Assign(name, value)
            
            self.error(equals, "Invalid assignment target.")
        return temp_expr
    
    def equality(self) -> expr.Expr:
        temp_expr = self.comparison()
        while (self.match(ts.TokenType.BANG_EQUAL, ts.TokenType.EQUAL_EQUAL)):
            operator = self.previous()
            right = self.comparison()
            temp_expr = expr.Binary(temp_expr, operator, right)
        return temp_expr
    
    def match(self, *tokens) -> bool:
        for token_type in tokens:
            if (self.check(token_type)):
                self.advance()
                return True

        return False
    
    def check(self, type) -> bool:
        if (self.is_at_end()):
            return False
        peeked_type = self.peek()
        return peeked_type.type == type
    
    def advance(self) -> ts.Token:
        if (not self.is_at_end()):
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
        while (self.match(ts.TokenType.GREATER, ts.TokenType.GREATER_EQUAL,
            ts.TokenType.LESS, ts.TokenType.LESS_EQUAL)):
            operator = self.previous()
            right = self.term()
            temp_expr = expr.Binary(temp_expr, operator, right)
        return temp_expr

    def term(self) -> expr.Expr:
        temp_expr = self.factor()
        while (self.match(ts.TokenType.MINUS, ts.TokenType.PLUS)):
            operator = self.previous()
            right = self.factor()
            temp_expr = expr.Binary(temp_expr, operator, right)
        return temp_expr

    def factor(self) -> expr.Expr:
        temp_expr = self.unary()
        while (self.match(ts.TokenType.SLASH, ts.TokenType.STAR)):
            operator = self.previous()
            right = self.unary()
            temp_expr = expr.Binary(temp_expr, operator, right)
        return temp_expr

    def unary(self) -> expr.Expr:
        if (self.match(ts.TokenType.BANG, ts.TokenType.MINUS)):
            operator = self.previous()
            right = self.unary()
            return expr.Unary(operator, right)
        else:
            return self.primary()
        
    def primary(self) -> expr.Expr:
        if (self.match(ts.TokenType.FALSE)):
            return expr.Literal(False)
        if (self.match(ts.TokenType.TRUE)):
            return expr.Literal(True)
        if (self.match(ts.TokenType.NIL)):
            return expr.Literal(None)
        
        if (self.match(ts.TokenType.NUMBER, ts.TokenType.STRING)):
            return expr.Literal(self.previous().literal)

        if (self.match(ts.TokenType.IDENTIFIER)):
            return expr.Variable(self.previous())
    
        if (self.match(ts.TokenType.LEFT_PAREN)):
            temp_expr = self.expression()
            self.consume(ts.TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return expr.Grouping(temp_expr)
        
        raise self.error(self.peek(), "Expect expression.")
    
    def consume(self,type: ts.TokenType, message: str):
        if self.check(type):
            return self.advance()
        
        raise self.error(self.peek(), message)
    
    def error(self, token: ts.Token, message: str):
        main_scanner.error(token, message)
        return Parser.ParseError() 

    def sychronize(self):
        self.advance()
        while (not self.is_at_end):
            if (self.previous().type == ts.TokenType.SEMICOLON):
                return
            
            if (self.peek().type == ts.TokenType.CLASS or 
                self.peek().type == ts.TokenType.FOR or
                self.peek().type == ts.TokenType.FUN or
                self.peek().type == ts.TokenType.IF or
                self.peek().type == ts.TokenType.PRINT or
                self.peek().type == ts.TokenType.RETURN or
                self.peek().type == ts.TokenType.VAR or
                self.peek().type == ts.TokenType.WHILE):
                return
        
        self.advance()