from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Iterator

from .parse_exception import ParseException
from .token_types import TokenType


@dataclass
class Token:
    type: TokenType
    value: str
    start_index: int


class TokenStream:
    def __init__(self) -> None:
        self._tokens: deque[Token] = deque()
        self._last_string_index = 0

    @property
    def current(self) -> Token | None:
        return self._tokens[0] if self._tokens else None

    @property
    def look_ahead(self) -> Token | None:
        return self._tokens[1] if len(self._tokens) > 1 else None

    @property
    def look_ahead_ignore_newlines(self) -> Token | None:
        index = 0
        while index < len(self._tokens) and self._tokens[index].type == TokenType.NEW_LINE:
            index += 1
        index += 1
        return self._tokens[index] if index < len(self._tokens) else None

    @property
    def last(self) -> Token | None:
        return self._tokens[-1] if self._tokens else None

    @property
    def current_string_end_index(self) -> int:
        if self.current is None:
            return self._last_string_index
        return self.current.start_index + len(self.current.value)

    @property
    def current_string_start_index(self) -> int:
        if self.current is None:
            return self._last_string_index
        return self.current.start_index

    def add(self, token: Token) -> None:
        self._tokens.append(token)
        self._last_string_index = token.start_index + len(token.value)

    def consume(self, token_type: TokenType = TokenType.NO_TOKEN, error: str | None = None, move_error_back: bool = False) -> Token:
        current = self.current
        if current is None:
            message = error or f"unexpected token {token_type.name}"
            raise ParseException(message, self._last_string_index, self._last_string_index)
        if token_type != TokenType.NO_TOKEN and current.type != token_type:
            newline_adjust = 1 if current.type == TokenType.NEW_LINE else 0
            start = current.start_index - (1 if move_error_back else 0) + newline_adjust
            end = current.start_index + (0 if move_error_back else len(current.value))
            message = error or f"unexpected token {token_type.name}"
            raise ParseException(message, start, end)
        self._tokens.popleft()
        return current

    def remove_last(self) -> None:
        if self._tokens:
            self._tokens.pop()
        self._last_string_index = self.last.start_index + len(self.last.value) if self.last else 0

    def __iter__(self) -> Iterator[Token]:
        return iter(self._tokens)

    def iterate_reverse(self) -> Iterator[Token]:
        for token in reversed(self.to_list()):
            yield token

    def to_list(self) -> list[Token]:
        return list(self._tokens)

    def get_last_new_line(self, pos: int) -> Token | None:
        token_index = self._token_index_at_pos(pos)
        index = (token_index - 1) if token_index is not None else (len(self._tokens) - 1)
        tokens = self.to_list()
        while index >= 0:
            if tokens[index].type == TokenType.NEW_LINE:
                return tokens[index]
            index -= 1
        return None

    def get_token_at_pos(self, pos: int) -> Token:
        token_index = self._token_index_at_pos(pos)
        if token_index is None:
            raise IndexError(pos)
        return self.to_list()[token_index]

    def _token_index_at_pos(self, pos: int) -> int | None:
        tokens = self.to_list()
        index = 0
        while index < len(tokens) and tokens[index].start_index + len(tokens[index].value) <= pos:
            index += 1
        if index >= len(tokens):
            return None
        return index

    def __str__(self) -> str:
        parts = []
        for token in self._tokens:
            parts.append(f" {token.value} {token.type.name} |".replace("\n", "\\n").replace("\t", "\\t"))
        return "".join(parts)
