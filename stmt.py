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
    def visit_expression_stmt(self, stmt):
        ...

    @abstractmethod
    def visit_function_stmt(self, stmt):
        ...

    @abstractmethod
    def visit_print_stmt(self, stmt):
        ...

    @abstractmethod
    def visit_var_stmt(self, stmt):
        ...

    @abstractmethod
    def visit_if_stmt(self, stmt):
        ...

    @abstractmethod
    def visit_while_stmt(self, stmt):
        ...

    @abstractmethod
    def visit_return_stmt(self, stmt):
        ...


class If(Stmt):
    def __init__(self, condition: Expr, thenBranch: Stmt, elseBranch: Stmt):
        self.condition = condition
        self.thenBranch = thenBranch
        self.elseBranch = elseBranch

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_if_stmt(self)


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


class Function(Stmt):
    def __init__(self, name: Token, params: List[Token], body: List[Stmt]):
        self.name = name
        self.params = params
        self.body = body

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_function_stmt(self)


class Print(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_print_stmt(self)


class Return(Stmt):
    def __init__(self, keyword: Token, value: Expr):
        self.keyword = keyword
        self.value = value

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_return_stmt(self)


class Var(Stmt):
    def __init__(self, name: Token, initializer: Expr):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_var_stmt(self)


class While(Stmt):
    def __init__(self, condition: Expr, body: Stmt):
        self.condition = condition
        self.body = body

    def accept(self, visitor: StmtVisitor):
        return visitor.visit_while_stmt(self)
