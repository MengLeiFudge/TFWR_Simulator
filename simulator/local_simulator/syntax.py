"""先检查原版游戏语法，再应用解析后的无意义表达式规则。"""
import ast
from bisect import bisect_left, bisect_right
import io
import tokenize

from .catalog import Direction, Entities, Grounds, Hats, Items, Leaderboards, Unlocks
from .game_parser import GameSyntaxError, validate_grammar


class SyntaxChecks(ast.NodeVisitor):
    """对齐三个CheckForNonsensicalCode覆写及赋值目标，不作常量传播。"""

    def __init__(self, source, filename, function_names=()):
        self.function_names = frozenset(function_names)
        self.variables = [set()]
        self.global_variables = [set()]
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

    def check_target(self, node):
        if isinstance(node, (ast.Tuple, ast.List)):
            for child in node.elts:
                self.check_target(child)
        elif isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Slice):
            self.fail(node, 'error_invalid_assign_expr', '游戏不支持给切片赋值；请逐项修改。')
        elif isinstance(node, ast.Name):
            constants = {'Entities', 'Grounds', 'Hats', 'Items', 'Leaderboards', 'Unlocks'}
            if node.id in constants or node.id in Direction.__members__:
                self.fail(node, 'error_invalid_assign_expr', '游戏常量不能作为赋值目标。')
            if node.id not in self.global_variables[-1]:
                self.variables[-1].add(node.id)

    def visit_Assign(self, node):
        for target in node.targets:
            self.check_target(target)
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        self.check_target(node.target)
        self.generic_visit(node)

    def visit_For(self, node):
        self.check_target(node.target)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        for default in node.args.defaults:
            self.visit(default)
        self.variables.append({argument.arg for argument in node.args.args})
        self.global_variables.append(set())
        for statement in node.body:
            self.visit(statement)
        self.variables.pop()
        self.global_variables.pop()
        if node.name not in self.global_variables[-1]:
            self.variables[-1].add(node.name)

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name != '*' and alias.name not in self.global_variables[-1]:
                self.variables[-1].add(alias.name)

    visit_ImportFrom = visit_Import

    def visit_Global(self, node):
        for name in node.names:
            if name in self.variables[-1]:
                self.fail(node, 'error_assign_before_global', '同一作用域内必须先声明global，再赋值。')
            self.global_variables[-1].add(name)

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Name) and node.value.id in self.function_names:
            self.fail(node.value, 'error_not_a_statement2', '内置函数作为语句时必须带调用括号。')
        self.generic_visit(node)

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


def validate_syntax(tree, source, filename, function_names=()):
    validate_grammar(source, filename)
    SyntaxChecks(source, filename, function_names).visit(tree)
