from __future__ import annotations
import runtime_error
import tokens as ts
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    import lox_class


class LoxInstance:
    def __init__(self, klass: lox_class.LoxClass):
        self.klass = klass
        self.fields = {}

    def __repr__(self) -> str:
        return self.klass.name + " instance"

    def get(self, name: ts.Token) -> Any:
        if self.fields.get(name.lexeme) is not None:
            return self.fields.get(name.lexeme)

        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)

        raise runtime_error.RuntimeError(
            self.name, "Undefined property '" + name.lexeme + "'."
        )

    def set(self, name: ts.Token, value: Any) -> Any:
        self.fields[name.lexeme] = value
