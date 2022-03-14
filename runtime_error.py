import tokens as ts


class RuntimeError(Exception):
    def __init__(self, token: ts.Token, message: str):
        self.message = message
        self.token = token
