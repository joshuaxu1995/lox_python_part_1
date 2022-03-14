from tokenize import Token
import main_scanner
import expr
import stmt
import tokens as ts
import environment
from typing import List, Optional, Any

class RuntimeError(Exception):
    def __init__(self, token: ts.Token, message: str):
        super(message)
        self.token = token

class Interpreter(expr.Visitor, stmt.StmtVisitor):

    def __init__(self):
        self.environment = environment.Environment()

    def interpret(self, statements: List[stmt.Stmt]):
        try:
            for statement in statements:
                self.execute(statement)
        except RuntimeError as e:
            main_scanner.runtime_error(e)
    
    def execute(self, stmt: stmt.Stmt) -> None:
        stmt.accept(self)

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
    
    def visit_expression_stmt(self, stmt: stmt.Expression) -> None:
        self.evaluate(stmt.expression)
        return
    
    def visit_print_stmt(self, stmt: stmt.Print) -> None:
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))
        return
    
    def visit_block_stmt(self, stmt: stmt.Block) -> None:
        self.execute_block(stmt.statements, environment.Environment(self.environment))
        return None

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
        self.environment.assign(expr.name, value)
        return value

    def visit_variable_expr(self, expr: expr.Variable):
        return self.environment.get(expr.name)

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
            raise RuntimeError(expr.operator, "Operands must be two numbers or two strings")
            
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
        raise RuntimeError(operator, "Operand must be a number")

    def check_number_operands(self, operator: ts.Token, left, right):
        if isinstance(left, int) or isinstance(left, float) and \
        isinstance(right, int) or isinstance(right, float):
            return
        raise RuntimeError(operator, "Operands must be numbers")

    
    def is_truthy(self, object: Any) -> bool:
        return bool(object)