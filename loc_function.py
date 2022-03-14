
from environment import Environment
from lox_callable import LoxCallable
import stmt
import return_exception_type
from typing import Any, List

class LoxFunction(LoxCallable):
    def __init__(self, declaration: stmt.Function, closure: Environment):
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter, arguments: List[Any]):
        environment = Environment(self.closure)
        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except return_exception_type.Return as r:
            return r.value
        return None

    def arity(self) -> int:
        return len(self.declaration.params)
    
    def to_string(self) -> str:
        return "<fn {self.declaration.name.lexeme}>"

