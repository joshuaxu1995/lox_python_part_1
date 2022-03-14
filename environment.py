from __future__ import annotations
from dis import dis
import tokens as ts
import runtime_error
from typing import Any


class Environment():
    def __init__(self, enclosing: Environment = None):
        self.enclosing = enclosing
        self.values = {}

    def get(self, name: ts.Token) -> Any:
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if (self.enclosing is not None):
            return self.enclosing.get(name)

        raise runtime_error.RuntimeError(
            name, "Undefined variable '" + name.lexeme + "'.")

    def get_at(self, distance: int, name: ts.Token) -> Any:
        return self.ancestor(distance).get(name)

    def assign_at(self, distance: int, name: ts.Token, value: Any) -> None:
        self.ancestor(distance).values[name.lexeme] = value

    def ancestor(self, distance: int) -> Environment:
        environment = self
        for i in range(distance):
            environment = environment.enclosing

        return environment

    def define(self, name: str, value: Any) -> None:
        self.values[name] = value

    def assign(self, name: ts.Token, value: Any) -> None:
        if (name.lexeme in self.values):
            self.values[name.lexeme] = value
            return

        if (self.enclosing is not None):
            self.enclosing.assign(name, value)
            return None

        raise runtime_error.RuntimeError(
            name, "Undefined variable '" + name.lexeme + "'.")
