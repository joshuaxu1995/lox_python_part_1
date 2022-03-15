import enum
import expr
import stmt
import interpreter
import collections
import main_scanner
from typing import List

from tokens import Token


class FunctionType(enum.Enum):
    NONE = 0
    FUNCTION = 1
    INITIALIZER = 2
    METHOD = 3

class ClassType(enum.Enum):
    NONE = 0
    SUBCLASS = 1
    CLASS = 1

class Resolver(expr.Visitor, stmt.StmtVisitor):

    def __init__(self, interpreter: interpreter.Interpreter):
        self.interpreter = interpreter
        self.scopes = collections.deque()
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE

    def visit_block_stmt(self, stmt: stmt.Block) -> None:
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()
        return None
    
    def visit_class_stmt(self, stmt: stmt.Class) -> None:
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS

        self.declare(stmt.name)
        self.define(stmt.name)

        if (stmt.superclass is not None and stmt.name.lexeme == stmt.superclass.name.lexeme):
            main_scanner.error(stmt.superclass.name, "A class can't inherit from itself.")

        if (stmt.superclass is not None):
            self.current_class = ClassType.SUBCLASS
            self.resolve_expr(stmt.superclass)
        
        if (stmt.superclass is not None):
            self.begin_scope()
            self.scopes[-1]["super"] = True

        self.begin_scope()
        self.scopes[-1]["this"] = True

        for method in stmt.methods:
            declaration = FunctionType.METHOD
            if (method.name.lexeme == "init"):
                declaration = FunctionType.INITIALIZER

            self.resolve_function(method, declaration)
    
        self.end_scope()
    
        if (stmt.superclass is not None):
            self.end_scope()

        self.current_class = enclosing_class
        return None

    def visit_expression_stmt(self, stmt: stmt.Expression):
        self.resolve_expr(stmt.expression)

    def visit_if_stmt(self, stmt: stmt.If):
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.thenBranch)
        if (stmt.elseBranch is not None):
            self.resolve_stmt(stmt.elseBranch)
        return None

    def visit_print_stmt(self, stmt: stmt.Print):
        self.resolve_expr(stmt.expression)
        return None

    def visit_return_stmt(self, stmt: stmt.Return):
        if (self.current_function == FunctionType.NONE):
            main_scanner.error(
                stmt.keyword, "Can't return from top-level code.")

        if (stmt.value is not None):
            if (self.current_function == FunctionType.INITIALIZER):
                main_scanner.error(stmt.keyword, "Can't return a value from an initializer.")
            self.resolve_expr(stmt.value)
        return None

    def visit_while_stmt(self, stmt: stmt.While):
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.body)
        return None

    def visit_binary_expr(self, expr: expr.Binary):
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)
        return None

    def visit_call_expr(self, expr: expr.Call):
        for argument in expr.arguments:
            self.resolve_expr(argument)
        self.resolve_expr(expr.callee)
    
    def visit_get_expr(self, expr: expr.Get):
        self.resolve_expr(expr.object)
        return None

    def visit_grouping_expr(self, expr: expr.Grouping):
        self.resolve_expr(expr.expression)
        return None

    def visit_literal_expr(self, expr: expr.Literal):
        return None

    def visit_logical_expr(self, expr: expr.Logical):
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)
        return None

    def visit_set_expr(self, expr: expr.Set):
        self.resolve_expr(expr.value)
        self.resolve_expr(expr.object)
        return None
    
    def visit_super_expr(self, expr: expr.Super):
        if (self.current_class is ClassType.NONE):
            main_scanner.error(expr.keyword, "Can't use 'super' outside of a class.")
        elif (self.current_class is not ClassType.SUBCLASS):
            main_scanner.error(expr.keyword, "Can't use 'super' in a class with no superclass.")

        self.resolve_local(expr, expr.keyword)
        return None

    def visit_this_expr(self, expr: expr.This):
        if (self.current_class is ClassType.NONE):
            main_scanner.error(expr.keyword, "Can't use 'this' outside of a class.")
            return None

        self.resolve_local(expr, expr.keyword)
        return None

    def visit_unary_expr(self, expr: expr.Unary):
        self.resolve(expr.right)
        return None

    def visit_var_stmt(self, stmt: stmt.Var) -> None:
        self.declare(stmt.name)
        if (stmt.initializer != None):
            self.resolve_expr(stmt.initializer)
        self.define(stmt.name)
        return None

    def visit_variable_expr(self, expr: expr.Variable) -> None:
        if (self.scopes and self.scopes[-1].get(expr.name.lexeme) == False):
            main_scanner.error(
                expr.name, "Can't read local variable in its own initializer.")

        self.resolve_local(expr, expr.name)
        return None

    def visit_assign_expr(self, expr: expr.Assign) -> None:
        self.resolve_expr(expr.value)
        self.resolve_local(expr, expr.name)
        return None

    def visit_function_stmt(self, stmt: stmt.Function) -> None:
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt, FunctionType.FUNCTION)
        return None

    def resolve(self, statements: List[stmt.Stmt]) -> None:
        for statement in statements:
            self.resolve_stmt(statement)

    def resolve_stmt(self, stmt: stmt.Stmt) -> None:
        stmt.accept(self)

    def resolve_expr(self, expr: expr.Expr) -> None:
        expr.accept(self)

    def resolve_function(self, func: stmt.Function, type: FunctionType) -> None:
        enclosing_function = self.current_function
        self.current_function = type

        self.begin_scope()
        for param in func.params:
            self.declare(param)
            self.define(param)

        self.resolve(func.body)
        self.end_scope()
        self.current_function = enclosing_function

    def begin_scope(self) -> None:
        self.scopes.append({})

    def end_scope(self) -> None:
        self.scopes.pop()

    def declare(self, name: Token) -> None:
        if (not len(self.scopes)):
            return
        curr_scope = self.scopes[-1]

        if (name.lexeme in curr_scope):
            main_scanner.error(
                name, "Already a variable with this name in the scope")

        curr_scope[name.lexeme] = False

    def define(self, name: Token) -> None:
        if (not len(self.scopes)):
            return
        self.scopes[-1][name.lexeme] = True

    def resolve_local(self, expr: expr.Expr, name: Token) -> None:
        for i in reversed(range(len(self.scopes))):
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return None
