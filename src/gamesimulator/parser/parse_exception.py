from __future__ import annotations


class ParseException(Exception):
    def __init__(self, message: str, start_index: int, end_index: int):
        super().__init__(message)
        self.start_index = start_index
        self.end_index = end_index
