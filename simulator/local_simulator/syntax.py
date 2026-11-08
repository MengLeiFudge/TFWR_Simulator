"""对齐已实现的游戏语法与无意义表达式检查；保留括号节点对规则的影响。"""
import ast
from bisect import bisect_left, bisect_right
import io
import tokenize

from .catalog import Direction, Entities, Grounds, Hats, Items, Leaderboards, Unlocks


class GameSyntaxError(SyntaxError):
    def __init__(self, code, message, location):
        super().__init__(message, location)
        self.code = code


class SyntaxChecks(ast.NodeVisitor):
    """校验调用参数语法与三个CheckForNonsensicalCode覆写，不作常量传播。"""

    def __init__(self, source, filename):
        self.filename = filename
        self.lines = source.splitlines(keepends=True)
        ignored = {tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT,
                   tokenize.DEDENT, tokenize.ENDMARKER}
        self.tokens = [token for token in tokenize.generate_tokens(io.StringIO(source).readline)
                       if token.type not in ignored]
        self.starts = [token.start for token in self.tokens]
        self.ends = [token.end for token in self.tokens]

    def position(self, node, end=False):
        # AST列号是UTF-8字节偏移，tokenize和SyntaxError使用字符列号。
        line = node.end_lineno if end else node.lineno
        column = node.end_col_offset if end else node.col_offset
        return line, len(self.lines[line - 1].encode('utf-8')[:column].decode('utf-8'))

    def wrapped(self, node):
        before = bisect_right(self.ends, self.position(node)) - 1
        after = bisect_left(self.starts, self.position(node, end=True))
        return (before >= 0 and after < len(self.tokens)
                and self.tokens[before].string == '(' and self.tokens[after].string == ')')

    def literal_kind(self, node):
        if self.wrapped(node):
            return None
        if isinstance(node, ast.Constant):
            return 'number' if type(node.value) in (int, float) else 'literal'
        namespaces = {'Entities': Entities, 'Grounds': Grounds, 'Hats': Hats,
                      'Items': Items, 'Leaderboards': Leaderboards, 'Unlocks': Unlocks}
        if isinstance(node, ast.Name):
            if node.id in namespaces or node.id in Direction.__members__:
                return 'literal'
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            name = node.value.id
            if name in namespaces and hasattr(namespaces[name], node.attr):
                return {'Items': 'item', 'Entities': 'entity', 'Grounds': 'ground',
                        'Unlocks': 'unlock'}.get(name, 'literal')
        return None

    def fail(self, node, code, message, operator=None):
        start, end = self.position(node), self.position(node, end=True)
        if operator is not None:
            start, end = operator.start, operator.end
        location = (self.filename, start[0], start[1] + 1, self.lines[start[0] - 1],
                    end[0], end[1] + 1)
        raise GameSyntaxError(code, message, location)

    def visit_Call(self, node):
        self.generic_visit(node)
        if node.keywords:
            keyword = node.keywords[0]
            begin = bisect_left(self.starts, self.position(keyword))
            end = bisect_left(self.starts, self.position(keyword.value))
            operator = next((token for token in self.tokens[begin:end] if token.string in ('=', '**')), None)
            code = 'error_expected_close_token' if keyword.arg is not None else 'error_invalid_expression'
            self.fail(keyword, code, '游戏函数调用只支持位置参数；请按参数顺序传值。', operator)

    def visit_BoolOp(self, node):
        self.generic_visit(node)
        if not isinstance(node.op, ast.Or):
            return
        # 游戏把连续or按左结合二元节点处理，只有首对的左边可能直接是比较。
        left, right = node.values[:2]
        if not isinstance(left, ast.Compare) or self.wrapped(left) or self.literal_kind(right) is None:
            return
        begin = bisect_left(self.starts, self.position(left, end=True))
        end = bisect_left(self.starts, self.position(right))
        operator = next((token for token in self.tokens[begin:end] if token.string == 'or'), None)
        self.fail(node, 'error_nonsensical_or',
                  f'比较表达式后的or不能直接接常量 {ast.unparse(right)}；请检查比较优先级和原条件。', operator)

    def check_condition(self, node):
        kind = self.literal_kind(node.test)
        if kind in ('item', 'entity', 'ground', 'unlock'):
            self.fail(node.test, f'error_{kind}_condition',
                      f'{ast.unparse(node.test)}是游戏常量，不能直接作为条件。')

    def visit_If(self, node):
        self.generic_visit(node)
        self.check_condition(node)

    def visit_While(self, node):
        self.generic_visit(node)
        self.check_condition(node)

    def visit_Compare(self, node):
        self.generic_visit(node)
        operands = [node.left, *node.comparators]
        for operator, left, right in zip(node.ops, operands, operands[1:]):
            left_kind, right_kind = self.literal_kind(left), self.literal_kind(right)
            if left_kind in ('item', 'entity', 'unlock'):
                kind, other = left_kind, right_kind
            elif right_kind in ('item', 'entity', 'unlock'):
                kind, other = right_kind, left_kind
            else:
                break
            if isinstance(operator, (ast.Eq, ast.NotEq, ast.In, ast.NotIn)) and other != 'number':
                return
            self.fail(node, f'error_compared_{kind}_with_number',
                      f'{ast.unparse(node)}不能把物品、实体或科技常量当作数量比较。')


def validate_syntax(tree, source, filename):
    SyntaxChecks(source, filename).visit(tree)
