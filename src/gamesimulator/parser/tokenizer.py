from __future__ import annotations

import re

from .token_stream import Token, TokenStream
from .token_types import TokenType


CONSTANT_TOKENS: list[tuple[str, bool, TokenType]] = [
    ("if", True, TokenType.IF),
    ("else", True, TokenType.ELSE),
    ("for", True, TokenType.FOR),
    ("or", True, TokenType.OR),
    ("and", True, TokenType.AND),
    ("return", True, TokenType.RETURN),
    ("def", True, TokenType.DEF),
    ("while", True, TokenType.WHILE),
    ("elif", True, TokenType.ELIF),
    ("break", True, TokenType.BREAK),
    ("continue", True, TokenType.CONTINUE),
    ("pass", True, TokenType.PASS),
    ("**", False, TokenType.EXP),
    ("==", False, TokenType.COMPARE),
    ("=", False, TokenType.ASSIGN),
    ("!=", False, TokenType.COMPARE),
    ("<=", False, TokenType.COMPARE),
    (">=", False, TokenType.COMPARE),
    ("<", False, TokenType.COMPARE),
    (">", False, TokenType.COMPARE),
    ("(", False, TokenType.BRACKET_OPEN),
    (")", False, TokenType.BRACKET_CLOSE),
    ("+=", False, TokenType.ASSIGN),
    ("+", False, TokenType.ADD),
    ("-=", False, TokenType.ASSIGN),
    ("->", False, TokenType.ARROW),
    ("-", False, TokenType.ADD),
    ("*=", False, TokenType.ASSIGN),
    ("//=", False, TokenType.ASSIGN),
    ("//", False, TokenType.MULT),
    ("/=", False, TokenType.ASSIGN),
    ("%=", False, TokenType.ASSIGN),
    ("*", False, TokenType.MULT),
    ("/", False, TokenType.MULT),
    ("%", False, TokenType.MULT),
    ("[", False, TokenType.SQUARE_BRACKET_OPEN),
    ("]", False, TokenType.SQUARE_BRACKET_CLOSE),
    ("{", False, TokenType.CURL_BRACE_OPEN),
    ("}", False, TokenType.CURL_BRACE_CLOSE),
    (",", False, TokenType.COMMA),
    (":", False, TokenType.COLON),
    ("|", False, TokenType.UNION),
    ("global", True, TokenType.GLOBAL),
    ("import", True, TokenType.IMPORT),
    ("from", True, TokenType.FROM),
]

REGEX_TOKENS: list[tuple[re.Pattern[str], TokenType]] = [
    (re.compile(r"(\d*\.)?\d+\b"), TokenType.NUM),
    (re.compile(r"(?:in|not\s+in)\b"), TokenType.IN),
    (re.compile(r"not\b"), TokenType.NOT),
    (re.compile(r"[a-zA-Z_]\w*"), TokenType.IDENTIFIER),
    (re.compile(r"(['\"])(.*?)\1"), TokenType.STRING),
    (re.compile(r"\n([ \t]*)"), TokenType.NEW_LINE),
    (re.compile(r"[^\S\n]+"), TokenType.IGNORE),
    (re.compile(r"#.*"), TokenType.IGNORE),
    (re.compile(r"\."), TokenType.DOT),
    (re.compile(r"\S+"), TokenType.UNKNOWN),
]


def tokenize(code: str) -> tuple[bool, TokenStream]:
    stream = TokenStream()
    stream.add(Token(TokenType.NEW_LINE, "\n", 0))
    has_unknown = False
    text = code.replace("\v", "\n")
    index = 0
    while index < len(text):
        matched = False
        for token_text, needs_word_boundary, token_type in CONSTANT_TOKENS:
            if not text.startswith(token_text, index):
                continue
            if needs_word_boundary and index + len(token_text) < len(text):
                next_char = text[index + len(token_text)]
                if next_char.isalnum() or next_char == "_":
                    continue
            stream.add(Token(token_type, token_text, index))
            index += len(token_text)
            matched = True
            break
        if matched:
            continue
        for pattern, token_type in REGEX_TOKENS:
            match = pattern.match(text, index)
            if not match:
                continue
            value = match.group(0)
            if token_type != TokenType.IGNORE:
                stream.add(Token(token_type, value, index))
            has_unknown = has_unknown or token_type == TokenType.UNKNOWN
            index += len(value)
            matched = True
            break
        if not matched:
            raise RuntimeError("nothing matched, not even UNKNOWN")
    while stream.last is not None and stream.last.type == TokenType.NEW_LINE:
        stream.remove_last()
    return has_unknown, stream
