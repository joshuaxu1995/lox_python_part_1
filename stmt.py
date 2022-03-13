from abc import ABC, abstractmethod
from tokens import Token
from expr import Expr
from typing import List

class StmtVisitor:
    pass

class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: StmtVisitor):
        ...

class StmtVisitor():
    
    @abstractmethod
    def visit_block_stmt(self, stmt):
        ...

    @abstractmethod
    def visit_expression_stmt(self, expr):
        ...
    
    @abstractmethod
    def visit_print_stmt(self, expr):
        ...
    
    @abstractmethod
    def visit_var_stmt(self, stmt):
        ...

class Block(Stmt):
    def __init__(self, statements: List[Stmt]):
        self.statements = statements

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_block_stmt(self)

class Expression(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_expression_stmt(self)

class Print(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_print_stmt(self)

class Var(Stmt):
    def __init__(self, name: Token, initializer: Expr):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_var_stmt(self)
