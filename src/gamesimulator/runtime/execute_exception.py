from __future__ import annotations


class ExecuteException(Exception):
    def __init__(self, message: str = "", start_index: int = -1, end_index: int = -1):
        super().__init__(message)
        self.start_index = start_index
        self.end_index = end_index


class BreakStatement(Exception):
    pass


class ContinueStatement(Exception):
    pass


class ReturnStatement(Exception):
    def __init__(self, start_index: int = -1, end_index: int = -1):
        super().__init__("return")
        self.start_index = start_index
        self.end_index = end_index
