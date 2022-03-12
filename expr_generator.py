from abc import ABC

class Expr(ABC):
    pass

def create_types():
    ast_types = {
        "Binary": ["left", "operator", "right"],
        "Grouping": ["expression"],
        "Literal": ["value"],
        "Unary": ["operator", "right"],
    }
    for ast_type, fields in ast_types.items():
        result = type(ast_type, (Expr,), fields)
        print(f'Printing result: {result}')

create_types()