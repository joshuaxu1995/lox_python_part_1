
from cmath import exp
from tokens import Token, TokenType
from typing import List
import main_scanner


class Scanner:

    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1

    keywords = {
        "and": TokenType.AND,
        "class": TokenType.CLASS,
        "else": TokenType.ELSE,
        "false": TokenType.FALSE,
        "for": TokenType.FOR,
        "fun": TokenType.FUN,
        "if": TokenType.IF,
        "nil": TokenType.NIL,
        "or": TokenType.OR,
        "print": TokenType.PRINT,
        "return": TokenType.RETURN,
        "super": TokenType.SUPER,
        "this": TokenType.THIS,
        "true": TokenType.TRUE,
        "var": TokenType.VAR,
        "while": TokenType.WHILE
    }

    def scanTokens(self) -> List[Token]:
        while (not self.is_at_end()):
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def scan_token(self):
        curr_char = self.advance()
        if curr_char == '(':
            self.add_token(TokenType.LEFT_PAREN)
        elif curr_char == ')':
            self.add_token(TokenType.RIGHT_PAREN)
        elif curr_char == '{':
            self.add_token(TokenType.LEFT_BRACE)
        elif curr_char == '}':
            self.add_token(TokenType.RIGHT_BRACE)
        elif curr_char == ',':
            self.add_token(TokenType.COMMA)
        elif curr_char == '.':
            self.add_token(TokenType.DOT)
        elif curr_char == '-':
            self.add_token(TokenType.MINUS)
        elif curr_char == '+':
            self.add_token(TokenType.PLUS)
        elif curr_char == ';':
            self.add_token(TokenType.SEMICOLON)
        elif curr_char == '*':
            self.add_token(TokenType.STAR)
        elif curr_char == '!':
            self.add_token(TokenType.BANG_EQUAL if self.match(
                '=') else TokenType.BANG)
        elif curr_char == '=':
            self.add_token(TokenType.EQUAL_EQUAL if self.match(
                '=') else TokenType.EQUAL)
        elif curr_char == '<':
            self.add_token(TokenType.LESS_EQUAL if self.match(
                '=') else TokenType.LESS)
        elif curr_char == '>':
            self.add_token(TokenType.GREATER_EQUAL if self.match(
                '=') else TokenType.GREATER)
        elif curr_char == '/':
            if (self.match('/')):
                while (self.peek() != '\n' and not self.is_at_end()):
                    self.advance()
            else:
                self.add_token(TokenType.SLASH)
        elif curr_char == ' ' or curr_char == '\r' or curr_char == '\t':
            pass
        elif curr_char == '\n':
            self.line += 1
        elif curr_char == '"':
            self.string_type()
        else:
            if (self.is_digit(curr_char)):
                self.number()
            elif (self.is_alpha(curr_char)):
                self.identifier()
            else:
                main_scanner.error_with_line(
                    self.line, "Unexpected character.")

    def is_digit(self, curr_char: str) -> bool:
        return curr_char >= '0' and curr_char <= '9'

    def number(self):
        while (self.is_digit(self.peek())):
            self.advance()

        if (self.peek() == '.' and self.is_digit(self.peek_next())):
            self.advance()

            while (self.is_digit(self.peek())):
                self.advance()

        self.add_token(TokenType.NUMBER, float(
            self.source[self.start: self.current]))

    def identifier(self):
        while (self.is_alphanumeric(self.peek())):
            self.advance()

        text = self.source[self.start: self.current]
        type = Scanner.keywords.get(text, None)
        if (type == None):
            type = TokenType.IDENTIFIER
        self.add_token(type)

    def is_alpha(self, c):
        return (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z') or c == '_'

    def is_alphanumeric(self, c):
        return self.is_alpha(c) or self.is_digit(c)

    def peek_next(self) -> str:
        if (self.current + 1 >= len(self.source)):
            return '\0'
        else:
            return self.source[self.current + 1]

    def string_type(self):
        while self.peek() != '"' and not self.is_at_end():
            if (self.peek() == '\n'):
                self.line += 1
            self.advance()

        if (self.is_at_end()):
            main_scanner.error_with_line(self.line, "Unterminated string.")
            return

        self.advance()

        value = self.source[self.start + 1: self.current - 1]
        self.add_token(TokenType.STRING, value)

    def peek(self) -> str:
        if (self.is_at_end()):
            return '\0'
        return self.source[self.current]

    def match(self, expected: str) -> bool:
        if (self.is_at_end()):
            return False
        if (self.source[self.current] != expected):
            return False

        self.current += 1
        return True

    def advance(self) -> str:
        curr_char = self.source[self.current]
        self.current += 1
        return curr_char

    def add_token(self, type: TokenType, literal=None) -> None:
        text = self.source[self.start: self.current]
        self.tokens.append(Token(type, text, literal, self.line))
