from __future__ import annotations

from typing import TYPE_CHECKING
from environment import Environment
from lox_callable import LoxCallable
import return_exception_type
from typing import Any, List
import tokens as ts

if TYPE_CHECKING:
    import stmt
    from lox_instance import LoxInstance


class LoxFunction(LoxCallable):
    def __init__(
            self,
            declaration: stmt.Function,
            closure: Environment,
            is_initializer: bool):
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer

    def bind(self, instance: LoxInstance):
        environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment, self.is_initializer)

    def call(self, interpreter, arguments: List[Any]):
        environment = Environment(self.closure)
        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except return_exception_type.Return as r:
            if (self.is_initializer):
                return self.closure.get_at(0, ts.Token(
                    ts.TokenType.THIS, "this", "DUMMY", -1))
            return r.value

        if self.is_initializer:
            return self.closure.get_at(0, ts.Token(
                ts.TokenType.THIS, "this", "DUMMY", -1))
        return None

    def arity(self) -> int:
        return len(self.declaration.params)

    def to_string(self) -> str:
        return "<fn {self.declaration.name.lexeme}>"
