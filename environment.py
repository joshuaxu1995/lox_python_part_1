from __future__ import annotations
import tokens as ts
import interpreter
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
        
        raise interpreter.RuntimeError(name, "Undefined variable '" + name.lexeme + "'.")
    
    def define(self, name: str, value: Any) -> None:
        self.values[name] = value

    def assign(self, name: ts.Token, value: Any) -> None:
        if (name.lexeme in self.values):
            self.values[name.lexeme] = value
            return
        
        if (self.enclosing is not None):
            self.enclosing.assign(name, value)
            return None

        raise interpreter.RuntimeError(name, "Undefined variable '" + name.lexeme + "'.")