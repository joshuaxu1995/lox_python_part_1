from tokenize import Token
import main_scanner
import expr
import tokens as ts

class RuntimeError(Exception):
    def __init__(self, token: ts.Token, message: str):
        super(message)
        self.token = token

class Interpreter(expr.Visitor):

    def interpret(self, curr_expr: expr.Expr):
        try:
            value = self.evaluate(curr_expr)
            print(self.stringify(value))
        except RuntimeError as e:
            main_scanner.runtime_error(e)
            
    
    def print(self, expr: expr.Expr) -> str:
        return expr.accept(self)

    def parenthesize(self, name: str, *expr_args) -> str:
        output_str_list = []
        output_str_list.append(f'({name}')
        for temp_expr in expr_args:
            output_str_list.append(f' {temp_expr.accept(self)}')
        output_str_list.append(")")
        return "".join(output_str_list)

    def visit_binary_expr(self, expr: expr.Binary) -> str:
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        if (expr.operator.type == ts.TokenType.GREATER):
            self.check_number_operands(expr.operator, left, right)
            return left > right
        elif expr.operator.type == ts.TokenType.GREATER_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return left >= right
        elif expr.operator.type == ts.TokenType.LESS:
            self.check_number_operands(expr.operator, left, right)
            return left < right
        elif expr.operator.type == ts.TokenType.LESS_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return left <= right
        elif expr.operator.type == ts.TokenType.BANG_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return not self.is_equal(left, right)
        elif expr.operator.type == ts.TokenType.EQUAL_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return self.is_equal(left, right)
        elif expr.operator.type == ts.TokenType.MINUS:
            self.check_number_operands(expr.operator, left, right)
            return left - right
        elif expr.operator.type == ts.TokenType.SLASH:
            self.check_number_operands(expr.operator, left, right)
            return left / right
        elif expr.operator.type == ts.TokenType.STAR:
            self.check_number_operands(expr.operator, left, right)
            return left * right
        elif expr.operator.type == ts.TokenType.PLUS:
            if (isinstance(left, float) or isinstance(left, int)) \
             and (isinstance(right, float) or isinstance(right, int)):
                return left + right
            elif isinstance(left, str) and isinstance(right, str):
                return left + right
            raise RuntimeError(expr.operator, "Operands must be two numbers or two strings")
            
    def is_equal(self, a, b) -> bool:
        if a is None or b is None: 
            return True
        
        if a is None:
            return False
        
        return a == b

    def stringify(self, object) -> str:
        if object is None:
            return None
        return str(object)

    def visit_grouping_expr(self, expr: expr.Grouping) -> str:
        return self.evaluate(expr.expression)
    
    def evaluate(self, expr: expr.Expr) -> any:
        return expr.accept(self)

    def visit_literal_expr(self, expr: expr.Literal) -> str:
        return expr.value

    def visit_unary_expr(self, expr: expr.Unary) -> str:
        right = self.evaluate(expr.right)

        if expr.operator.type == ts.TokenType.BANG:
            return not self.is_truthy(right)
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

    
    def is_truthy(self, object: any) -> bool:
        return bool(object)