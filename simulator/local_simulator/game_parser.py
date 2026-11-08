"""按Core.Parser与Tokenizer检查游戏源语法，独立于CPython执行后端。"""
from bisect import bisect_right
from dataclasses import dataclass
import re


class GameSyntaxError(SyntaxError):
    def __init__(self, code, message, location):
        super().__init__(message, location)
        self.code = code


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    start: int
    end: int


# 顺序与Tokenizer.constantTokens一致：长运算符必须先于其短前缀。
CONSTANTS = (
    ('if', 'IF'), ('else', 'ELSE'), ('for', 'FOR'), ('or', 'OR'), ('and', 'AND'),
    ('return', 'RETURN'), ('def', 'DEF'), ('while', 'WHILE'), ('elif', 'ELIF'),
    ('break', 'BREAK'), ('continue', 'CONTINUE'), ('pass', 'PASS'),
    ('**', 'EXP'), ('==', 'COMPARE'), ('=', 'ASSIGN'), ('!=', 'COMPARE'),
    ('<=', 'COMPARE'), ('>=', 'COMPARE'), ('<', 'COMPARE'), ('>', 'COMPARE'),
    ('(', '('), (')', ')'), ('+=', 'ASSIGN'), ('+', 'ADD'), ('-=', 'ASSIGN'),
    ('->', 'ARROW'), ('-', 'ADD'), ('*=', 'ASSIGN'), ('//=', 'ASSIGN'),
    ('//', 'MULT'), ('/=', 'ASSIGN'), ('%=', 'ASSIGN'), ('*', 'MULT'),
    ('/', 'MULT'), ('%', 'MULT'), ('[', '['), (']', ']'), ('{', '{'), ('}', '}'),
    (',', ','), (':', ':'), ('|', 'UNION'), ('global', 'GLOBAL'),
    ('import', 'IMPORT'), ('from', 'FROM'),
)
PATTERNS = tuple((re.compile(re.escape(text) + (r'\b' if text.isalpha() else '')), kind)
                 for text, kind in CONSTANTS) + (
    (re.compile(r'(\d*\.)?\d+\b'), 'NUM'),
    (re.compile(r'(?:in|not\s+in)\b'), 'IN'),
    (re.compile(r'not\b'), 'NOT'),
    (re.compile(r'[a-zA-Z_]\w*'), 'IDENTIFIER'),
    (re.compile(r"(['\"])(.*?)\1"), 'STRING'),
    (re.compile(r'\n[ \t]*'), 'NEW_LINE'),
    (re.compile(r'[^\S\n]+|#[^\n]*'), 'IGNORE'),
    (re.compile(r'\.'), '.'),
    (re.compile(r'\S+'), 'UNKNOWN'),
)
# 对应Parser.operators；NOT与第二个ADD层是一元运算，其余为二元或后缀。
OPERATORS = (('OR',), ('AND',), ('NOT',), ('COMPARE', 'IN'), ('ADD',),
             ('MULT',), ('ADD',), ('EXP',), ('(', '[', '.'))
MESSAGES = {
    'error_expected_close_token': '应为逗号或右括号；请使用游戏支持的表达式。',
    'error_invalid_expression': '游戏不支持此表达式。',
    'error_code_after_block': '语句后仍有游戏无法解析的代码；请使用游戏支持的语法。',
    'error_no_statements': '代码块必须换行并缩进，不能将语句写在冒号后同一行。',
    'error_not_enough_indentation': '代码块缺少缩进。',
    'error_too_much_indentation': '出现多余缩进。',
    'error_mixed_indentation': '同一缩进不能混用制表符与空格。',
    'error_missing_default_parameter': '带默认值的参数之后也必须提供默认值。',
    'error_invalid_import': '游戏导入只支持模块名，不支持路径或别名。',
    'error_invalid_number_format': '游戏数值只支持十进制整数或小数。',
}


class GameParser:
    """只解析语法，不执行脚本；错误保留原版错误码及源文件位置。"""

    def __init__(self, source, filename):
        self.source = source.replace('\v', '\n')
        self.filename = filename
        self.lines = self.source.splitlines(keepends=True)
        self.line_starts = [0] + [match.end() for match in re.finditer('\n', self.source)]
        self.tokens = [Token('NEW_LINE', '\n', 0, 0)]
        offset = 0
        while offset < len(self.source):
            for pattern, kind in PATTERNS:
                match = pattern.match(self.source, offset)
                if match:
                    if kind != 'IGNORE':
                        self.tokens.append(Token(kind, match.group(), offset, match.end()))
                    offset = match.end()
                    break
            else:
                raise ValueError('游戏词法检查未推进。')
        while self.tokens and self.tokens[-1].kind == 'NEW_LINE':
            self.tokens.pop()
        self.tokens.append(Token('EOF', '', len(self.source), len(self.source)))
        self.cursor = 0

    @property
    def current(self):
        return self.tokens[self.cursor]

    def fail(self, code, expected=None):
        token = self.current
        line = bisect_right(self.line_starts, token.start)
        end_line = bisect_right(self.line_starts, token.end)
        text = self.lines[line - 1] if line <= len(self.lines) else ''
        message = MESSAGES.get(code, f'游戏语法需要{expected or "其他表达式"}，当前为{token.value!r}。')
        location = (self.filename, line, token.start - self.line_starts[line - 1] + 1,
                    text, end_line, token.end - self.line_starts[end_line - 1] + 1)
        raise GameSyntaxError(code, message, location)

    def consume(self, kind, code='error_unexpected_token'):
        if self.current.kind != kind:
            self.fail(code, kind)
        token = self.current
        self.cursor += 1
        return token

    def line_breaks(self):
        while self.current.kind == 'NEW_LINE':
            self.cursor += 1

    def indentation(self):
        if self.current.kind != 'NEW_LINE':
            self.fail('error_new_line_expected')
        while self.tokens[self.cursor + 1].kind == 'NEW_LINE':
            self.cursor += 1
        value = self.current.value
        if '\t' in value and ' ' in value:
            self.fail('error_mixed_indentation')
        return value.count(' ') + value.count('\t') * 4

    def parse(self):
        self.block(-1, global_scope=True)
        if self.current.kind != 'EOF':
            self.fail('error_code_after_block')

    def block(self, previous, global_scope=False):
        if global_scope and self.current.kind == 'EOF':
            return
        if self.current.kind != 'NEW_LINE':
            self.fail('error_no_statements')
        indentation = self.indentation()
        if indentation <= previous:
            self.fail('error_not_enough_indentation')
        current = indentation
        while current == indentation:
            self.consume('NEW_LINE')
            self.statement(indentation, global_scope)
            if self.current.kind != 'NEW_LINE':
                break
            current = self.indentation()
        if current > indentation:
            self.fail('error_too_much_indentation')

    def statement(self, indentation, global_scope):
        kind = self.current.kind
        if kind == 'DEF':
            self.function(indentation)
        elif kind in ('PASS', 'BREAK', 'CONTINUE'):
            self.cursor += 1
        elif kind == 'RETURN':
            self.cursor += 1
            if self.current.kind not in ('NEW_LINE', 'EOF'):
                self.tuple_expression()
        elif kind == 'GLOBAL':
            self.cursor += 1
            self.consume('IDENTIFIER')
            self.variable_annotation()
        elif kind == 'IMPORT':
            self.cursor += 1
            self.identifiers('error_invalid_import')
        elif kind == 'FROM':
            self.cursor += 1
            self.consume('IDENTIFIER', 'error_invalid_import')
            self.consume('IMPORT', 'error_invalid_import')
            if self.current.value == '*':
                if not global_scope:
                    self.fail('error_wildcard_imports_not_allowed_in_function')
                self.consume('MULT')
            else:
                self.identifiers()
        elif kind in ('WHILE', 'FOR', 'IF'):
            self.flow(indentation)
        else:
            self.tuple_expression(end='ASSIGN', leftmost=True)
            if self.current.kind == 'ASSIGN':
                self.cursor += 1
                self.tuple_expression()

    def function(self, indentation):
        self.consume('DEF')
        self.consume('IDENTIFIER')
        if self.current.kind == '[':
            self.type_list()
        self.consume('(')
        self.line_breaks()
        default_seen = False
        while self.current.kind != ')':
            self.consume('IDENTIFIER')
            self.variable_annotation()
            self.line_breaks()
            if self.current.kind == 'ASSIGN':
                self.consume('ASSIGN')
                self.line_breaks()
                self.expression(line_breaks=True)
                default_seen = True
            elif default_seen:
                self.fail('error_missing_default_parameter')
            if self.current.kind != ',':
                break
            self.consume(',')
            self.line_breaks()
        self.consume(')')
        if self.current.kind == 'ARROW':
            self.consume('ARROW')
            self.type_expression()
        self.consume(':')
        self.block(indentation)

    def identifiers(self, code='error_unexpected_token'):
        if self.current.kind == '(':
            self.consume('(')
            self.line_breaks()
            self.consume('IDENTIFIER', code)
            self.line_breaks()
            while self.current.kind == ',':
                self.consume(',')
                self.line_breaks()
                if self.current.kind == ')':
                    break
                self.consume('IDENTIFIER', code)
                self.line_breaks()
            self.consume(')', code)
        else:
            self.consume('IDENTIFIER', code)
            while self.current.kind == ',':
                self.consume(',')
                self.consume('IDENTIFIER', code)
            if code == 'error_invalid_import' and self.current.kind not in ('NEW_LINE', 'EOF'):
                self.fail(code)

    def flow(self, indentation):
        kind = self.current.kind
        self.cursor += 1
        if kind == 'FOR':
            self.tuple_expression(end='IN')
            self.consume('IN', 'error_invalid_for_syntax')
        self.tuple_expression()
        if self.current.kind == 'ASSIGN':
            self.fail('error_unexpected_assign')
        self.consume(':')
        self.block(indentation)
        if kind in ('IF', 'ELIF') and self.current.kind == 'NEW_LINE':
            next_kind = self.tokens[self.cursor + 1].kind
            if next_kind in ('ELSE', 'ELIF') and self.indentation() == indentation:
                self.consume('NEW_LINE')
                if next_kind == 'ELSE':
                    self.consume('ELSE')
                    self.consume(':')
                    self.block(indentation)
                else:
                    self.flow(indentation)

    def variable_annotation(self):
        if self.current.kind == ':' and self.tokens[self.cursor + 1].kind in ('STRING', 'IDENTIFIER'):
            self.consume(':')
            self.type_expression()

    def type_expression(self, optional=False):
        if self.current.kind == 'STRING':
            self.consume('STRING')
            return
        if not optional or self.current.kind == 'IDENTIFIER':
            self.consume('IDENTIFIER')
        if self.current.kind == '[':
            self.type_list()
        if self.current.kind == 'UNION':
            self.consume('UNION')
            self.type_expression()

    def type_list(self):
        self.consume('[')
        if self.current.kind == '(':
            self.consume('(')
            self.consume(')')
        else:
            self.type_expression(optional=True)
            while self.current.kind == ',':
                self.consume(',')
                if self.current.kind == ']':
                    break
                self.type_expression(optional=True)
        self.consume(']')

    def tuple_expression(self, line_breaks=False, end=')', leftmost=False, started=False):
        if not started:
            if self.current.kind == end:
                return
            self.expression(line_breaks=line_breaks, exclude=end, leftmost=leftmost)
        if self.current.kind == ',':
            self.consume(',')
            self.sequence(end, line_breaks=line_breaks)

    def sequence(self, end, line_breaks=True, allow_pairs=False):
        if line_breaks:
            self.line_breaks()
        pairs = True
        count = 0
        while self.current.kind != end and (line_breaks or self.current.kind not in ('NEW_LINE', 'EOF')):
            self.expression(line_breaks=line_breaks, exclude=end)
            if line_breaks:
                self.line_breaks()
            if self.current.kind == ':':
                if not pairs or not allow_pairs:
                    self.fail('error_invalid_expression')
                self.consume(':')
                if line_breaks:
                    self.line_breaks()
                self.expression(line_breaks=line_breaks, exclude=end)
            else:
                if pairs and count:
                    self.fail('error_invalid_expression')
                pairs = False
            count += 1
            if line_breaks:
                self.line_breaks()
            comma = self.current.kind == ','
            if comma:
                self.consume(',')
                if line_breaks:
                    self.line_breaks()
            if self.current.kind == end or (not line_breaks and self.current.kind in ('NEW_LINE', 'EOF')):
                break
            if not comma:
                self.fail('error_expected_close_token' if line_breaks else 'error_invalid_expression')

    def expression(self, level=0, line_breaks=False, exclude=None, leftmost=False):
        if line_breaks:
            self.line_breaks()
        if level < len(OPERATORS) and exclude in OPERATORS[level]:
            level += 1
        if level == len(OPERATORS):
            self.atomic(leftmost)
            return
        operators = OPERATORS[level]
        if level in (2, 6):
            if self.current.kind in operators:
                self.cursor += 1
                self.expression(level, line_breaks)
            else:
                self.expression(level + 1, line_breaks, exclude, leftmost)
            return
        self.expression(level + 1, line_breaks, exclude, leftmost)
        if line_breaks:
            self.line_breaks()
        if level == 8:
            self.postfix()
        else:
            while self.current.kind in operators:
                self.cursor += 1
                self.expression(level + 1, line_breaks, exclude)
                if line_breaks:
                    self.line_breaks()

    def postfix(self):
        while self.current.kind in ('(', '[', '.'):
            kind = self.current.kind
            self.cursor += 1
            if kind == '(':
                self.sequence(')')
                self.consume(')')
            elif kind == '.':
                self.consume('IDENTIFIER')
            else:
                self.slice_index()
                if self.current.kind == ':':
                    self.consume(':')
                    self.slice_index(last=True)
                    if self.current.kind == ':':
                        self.consume(':')
                        self.line_breaks()
                        if self.current.kind != ']':
                            self.expression(line_breaks=True)
                self.line_breaks()
                self.consume(']')

    def slice_index(self, last=False):
        self.line_breaks()
        if self.current.kind != ':' and not (last and self.current.kind == ']'):
            self.expression(line_breaks=True)
            if self.current.kind != ':':
                self.tuple_expression(line_breaks=True, end=']', started=True)
        self.line_breaks()

    def atomic(self, annotated=False):
        kind = self.current.kind
        if kind == '(':
            self.consume('(')
            self.tuple_expression(line_breaks=True)
            self.line_breaks()
            self.consume(')')
        elif kind in ('[', '{'):
            self.cursor += 1
            end = ']' if kind == '[' else '}'
            self.sequence(end, allow_pairs=kind == '{')
            self.consume(end)
        elif kind in ('NUM', 'STRING', 'IDENTIFIER'):
            token = self.current
            self.cursor += 1
            if kind == 'NUM' and any(char not in '0123456789.' for char in token.value):
                self.cursor -= 1
                self.fail('error_invalid_number_format')
            if kind == 'IDENTIFIER' and annotated:
                self.variable_annotation()
        else:
            self.fail('error_invalid_expression')


def validate_grammar(source, filename):
    GameParser(source, filename).parse()
