from __future__ import annotations

from typing import TYPE_CHECKING
from lox_callable import LoxCallable
from typing import List, Any, Dict
from lox_instance import LoxInstance

if TYPE_CHECKING:
    import interpreter

class LoxClass(LoxCallable):
    def __init__(self, name: str, superclass: LoxClass, methods: Dict):
        self.name = name
        self.superclass = superclass
        self.methods = methods
    
    def find_method(self, name: str):
        if name in self.methods:
            return self.methods[name]
        
        if self.superclass is not None:
            return self.superclass.find_method(name)

        return None

    def __repr__(self) -> str:
        return self.name
    
    def call(self, interpreter: interpreter.Interpreter, arguments: List[Any]):
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if (initializer is not None):
            initializer.bind(instance).call(interpreter, arguments)
        return instance
    
    def arity(self) -> int:
        initializer = self.find_method("init")
        if (initializer is None):
            return 0
        return initializer.arity()