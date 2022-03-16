import expr
import tokens


class AstPrinter(expr.Visitor):
    def print(self, expr: expr.Expr) -> str:
        return expr.accept(self)

    def parenthesize(self, name: str, *expr_args) -> str:
        output_str_list = []
        output_str_list.append(f"({name}")
        for temp_expr in expr_args:
            output_str_list.append(f" {temp_expr.accept(self)}")
        output_str_list.append(")")
        return "".join(output_str_list)

    def visit_binary_expr(self, expr: expr.Binary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: expr.Grouping) -> str:
        return self.parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr: expr.Literal) -> str:
        if expr.value is None:
            return None
        return expr.value

    def visit_unary_expr(self, expr: expr.Unary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.right)


def execute_test():
    expression = expr.Binary(
        expr.Unary(
            tokens.Token(tokens.TokenType.MINUS, "-", None, 1), expr.Literal(123)
        ),
        tokens.Token(tokens.TokenType.STAR, "*", None, 1),
        expr.Grouping(expr.Literal(45.67)),
    )
    print(AstPrinter().print(expression))


if __name__ == "__main__":
    execute_test()
