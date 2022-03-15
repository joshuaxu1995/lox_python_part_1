from __future__ import annotations
from lox_function import LoxFunction
from lox_callable import LoxCallable
from lox_class import LoxClass
from lox_instance import LoxInstance
import main_scanner
import expr
import return_exception_type
import stmt
import tokens as ts
import environment
import runtime_error
from typing import List, Optional, Any
import time


class ClockLoxCallable(LoxCallable):

    def call(interpreter: Interpreter, arguments: List[Any]) -> Any:
        return round(time.time())

    def arity() -> int:
        return 0

    def to_string() -> str:
        return "clock: <native fn>"


class Interpreter(expr.Visitor, stmt.StmtVisitor):

    def __init__(self):
        self.globals = environment.Environment()
        self.environment = self.globals
        self.define_clock()
        self.locals = {}

    def define_clock(self):
        self.globals.define("clock", ClockLoxCallable)

    def interpret(self, statements: List[stmt.Stmt]):
        try:
            for statement in statements:
                self.execute(statement)
        except RuntimeError as e:
            main_scanner.runtime_error(e)

    def execute(self, stmt: stmt.Stmt) -> None:
        stmt.accept(self)

    def resolve(self, expr: expr.Expr, depth: int) -> None:
        self.locals[expr] = depth

    def execute_block(self, statements: List[stmt.Stmt], environment: environment.Environment) -> None:
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def print(self, expr: expr.Expr) -> str:
        return expr.accept(self)

    def parenthesize(self, name: str, *expr_args) -> str:
        output_str_list = []
        output_str_list.append(f'({name}')
        for temp_expr in expr_args:
            output_str_list.append(f' {temp_expr.accept(self)}')
        output_str_list.append(")")
        return "".join(output_str_list)

    def visit_function_stmt(self, stmt: stmt.Function) -> None:
        temp_function = LoxFunction(stmt, self.environment, False)
        self.environment.define(stmt.name.lexeme, temp_function)
        return None

    def visit_expression_stmt(self, stmt: stmt.Expression) -> None:
        self.evaluate(stmt.expression)
        return

    def visit_print_stmt(self, stmt: stmt.Print) -> None:
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))
        return

    def visit_return_stmt(self, stmt: stmt.Return) -> None:
        value = None
        if (stmt.value != None):
            value = self.evaluate(stmt.value)

        raise return_exception_type.Return(value)

    def visit_block_stmt(self, stmt: stmt.Block) -> None:
        self.execute_block(
            stmt.statements, environment.Environment(self.environment))
        return None

    def visit_class_stmt(self, stmt: stmt.Class) -> None:
        superclass = None
        if (stmt.superclass is not None):
            superclass = self.evaluate(stmt.superclass)
            if not isinstance(superclass, LoxClass):
                raise runtime_error.RuntimeError(stmt.superclass.name,
                    "Superclass must be a class.")


        self.environment.define(stmt.name.lexeme, None)

        if (stmt.superclass is not None):
            self.environment = environment.Environment(self.environment)
            self.environment.define("super", superclass)

        methods = {}
        for method in stmt.methods:
            temp_function = LoxFunction(method, self.environment, method.name.lexeme == "init")
            methods[method.name.lexeme] = temp_function
        
        klass = LoxClass(stmt.name.lexeme, superclass, methods)

        if (superclass is not None):
            self.environment = self.environment.enclosing

        self.environment.assign(stmt.name, klass)

    def visit_if_stmt(self, stmt: stmt.If) -> None:
        if (self.is_truthy(self.evaluate(stmt.condition))):
            self.execute(stmt.thenBranch)
        elif (stmt.elseBranch is not None):
            self.execute(stmt.elseBranch)
        else:
            return None

    def visit_while_stmt(self, stmt: stmt.While) -> None:
        while (self.is_truthy(self.evaluate(stmt.condition))):
            self.execute(stmt.body)
        return None

    def visit_var_stmt(self, stmt: stmt.Var) -> None:
        value = None
        if (stmt.initializer != None):
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)
        return None

    def visit_logical_expr(self, expr: expr.Logical):
        left = self.evaluate(expr.left)
        if (expr.operator.type == ts.TokenType.OR):
            if (self.is_truthy(left)):
                return left
        else:
            if (not self.is_truthy(left)):
                return left

        return self.evaluate(expr.right)

    def visit_assign_expr(self, expr: expr.Assign):
        value = self.evaluate(expr.value)

        distance = self.locals.get(expr)
        if (distance is not None):
            self.environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)

        return value

    def visit_variable_expr(self, expr: expr.Variable):
        return self.look_up_variable(expr.name, expr)

    def look_up_variable(self, name: ts.Token, expr: expr.Expr) -> Any:
        distance = self.locals.get(expr)
        if (distance != None):
            return self.environment.get_at(distance, name)
        else:
            return self.globals.get(name)

    def visit_binary_expr(self, expr: expr.Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        if (expr.operator.type == ts.TokenType.GREATER):
            self.check_number_operands(expr.operator, left, right)
            return float(left) > float(right)
        elif expr.operator.type == ts.TokenType.GREATER_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return float(left) >= float(right)
        elif expr.operator.type == ts.TokenType.LESS:
            self.check_number_operands(expr.operator, left, right)
            return float(left) < float(right)
        elif expr.operator.type == ts.TokenType.LESS_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return float(left) <= float(right)
        elif expr.operator.type == ts.TokenType.BANG_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return not self.is_equal(left, right)
        elif expr.operator.type == ts.TokenType.EQUAL_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return self.is_equal(left, right)
        elif expr.operator.type == ts.TokenType.MINUS:
            self.check_number_operands(expr.operator, left, right)
            return float(left) - float(right)
        elif expr.operator.type == ts.TokenType.SLASH:
            self.check_number_operands(expr.operator, left, right)
            return float(left) / float(right)
        elif expr.operator.type == ts.TokenType.STAR:
            self.check_number_operands(expr.operator, left, right)
            return float(left) * float(right)
        elif expr.operator.type == ts.TokenType.PLUS:
            if (isinstance(left, float) or isinstance(left, int)) \
                    and (isinstance(right, float) or isinstance(right, int)):
                return float(left) + float(right)
            elif isinstance(left, str) and isinstance(right, str):
                return left + right
            raise runtime_error.RuntimeError(
                expr.operator, "Operands must be two numbers or two strings")

    def visit_call_expr(self, expr: expr.Call) -> Any:
        callee = self.evaluate(expr.callee)
        arguments = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))

        temp_function = callee

        if (len(arguments) != temp_function.arity()):
            raise runtime_error.RuntimeError(
                expr.paren, f'Expected {temp_function.arity()} arguments but got {len(arguments)}.')

        if (not isinstance(callee, LoxCallable) and not issubclass(callee, LoxCallable)):
            raise runtime_error.RuntimeError(
                expr.paren, "can only call functions and classes.")

        return temp_function.call(self, arguments)
    
    def visit_get_expr(self, expr: expr.Get) -> Any:
        object = self.evaluate(expr.object)
        if isinstance(object, LoxInstance):
            return object.get(expr.name)
        
        raise runtime_error.RuntimeError(expr.name, "Only instances have properties.")

    def is_equal(self, a, b) -> bool:
        if a is None or b is None:
            return True

        if a is None:
            return False

        return a == b

    def stringify(self, object) -> Optional[str]:
        if object is None:
            return None
        return str(object)

    def visit_grouping_expr(self, expr: expr.Grouping) -> str:
        return self.evaluate(expr.expression)

    def evaluate(self, expr: expr.Expr) -> Any:
        return expr.accept(self)

    def visit_literal_expr(self, expr: expr.Literal) -> str:
        return expr.value
    
    def visit_set_expr(self, expr: expr.Set) -> Any:
        object = self.evaluate(expr.object)
        if not isinstance(object, LoxInstance):
            raise runtime_error.RuntimeError(expr.name, "Only instances have fields.")
        
        value = self.evaluate(expr.value)
        object.set(expr.name, value)

    def visit_super_expr(self, expr: expr.Super) -> Any:
        distance = self.locals.get(expr)
        superclass = self.environment.get_at(distance, ts.Token(ts.TokenType.SUPER, "super", "DUMMY", -1))

        object = self.environment.get_at(distance - 1, ts.Token(ts.TokenType.THIS, "this", "DUMMY", -1))
        method = superclass.find_method(expr.method.lexeme)

        if method is None:
            raise runtime_error.RuntimeError(expr.method, "Undefined property '" + expr.method.lexeme + "'.")

        return method.bind(object)
    
    def visit_this_expr(self, expr: expr.This) -> Any:
        return self.look_up_variable(expr.keyword, expr)

    def visit_unary_expr(self, expr: expr.Unary) -> Optional[str]:
        right = self.evaluate(expr.right)

        if expr.operator.type == ts.TokenType.BANG:
            return self.stringify(not self.is_truthy(right))
        elif expr.operator.type == ts.TokenType.MINUS:
            return -right
        else:
            return None

    def check_number_operand(self, operator: ts.Token, operand):
        if isinstance(operand, int) or isinstance(operand, float):
            return
        raise runtime_error.RuntimeError(operator, "Operand must be a number")

    def check_number_operands(self, operator: ts.Token, left, right):
        if isinstance(left, int) or isinstance(left, float) and \
                isinstance(right, int) or isinstance(right, float):
            return
        raise runtime_error.RuntimeError(operator, "Operands must be numbers")

    def is_truthy(self, object: Any) -> bool:
        return bool(object)
