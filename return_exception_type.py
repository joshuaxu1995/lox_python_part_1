from typing import Any


class Return(RuntimeError):
    def __init__(self, value: Any):
        self.value = value
