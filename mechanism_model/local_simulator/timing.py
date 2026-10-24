"""原版语法节点的操作计时；保留表达式求值顺序，在计费点让出执行。"""

import ast
import math
import operator


ARITHMETIC = {'Add': operator.add, 'Sub': operator.sub, 'Mult': operator.mul,
              'Div': operator.truediv, 'FloorDiv': operator.floordiv,
              'Mod': operator.mod, 'Pow': operator.pow}


def size(value):
    """原版哈希键大小：元组递归计数，字符串按一个对象计数。"""
    if isinstance(value, (tuple, list, set, dict)):
        return sum(size(item) for item in value)
    return 1


def equals(left, right, counter):
    """按原版深比较顺序累计访问量，包含失败比较和容器根节点。"""
    if counter[0] > 1000:
        raise ValueError('容器比较超过原版深度上限')
    counter[0] += 1
    if isinstance(left, (list, tuple)) and isinstance(right, (list, tuple, range)):
        return len(left) == len(right) and all(equals(a, b, counter) for a, b in zip(left, right))
    if isinstance(left, dict) and isinstance(right, dict):
        return len(left) == len(right) and all(k in right and equals(v, right[k], counter) for k, v in left.items())
    return left == right


def compare(left, right, counter):
    """原版排序比较先检查子项相等，再比较首个不等子项。"""
    if left is None and right is None:
        return 0
    if counter[0] > 1000:
        raise ValueError('容器比较超过原版深度上限')
    counter[0] += 1
    if isinstance(left, (list, tuple, range)) and isinstance(right, (list, tuple, range)):
        for a, b in zip(left, right):
            if not equals(a, b, counter):
                return compare(a, b, counter)
        return (len(left) > len(right)) - (len(left) < len(right))
    return (left > right) - (left < right)


def contains(value, collection, counter):
    """序列按检查项计费，哈希容器按键大小计费。"""
    if isinstance(collection, (dict, set)):
        counter[0] += size(value)
        return value in collection
    if isinstance(collection, range):
        counter[0] += 8
        return value in collection
    for item in collection:
        if equals(item, value, counter):
            return True
    return False


def index_value(collection, index):
    """原版序列接受数值索引，检查原始边界后向零截断。"""
    if isinstance(collection, dict) or isinstance(index, slice):
        return index
    if index < 0:
        index += len(collection)
    if not 0 <= index < len(collection):
        raise IndexError('序列索引越界')
    return int(index)


def operation(name, *args):
    """返回表达式结果和原版操作数；调用方在操作后结算时间。"""
    if name in ARITHMETIC or name.startswith('Aug'):
        augmented = name.startswith('Aug')
        op = name[3:] if augmented else name
        left, right = args
        if op == 'Add' and isinstance(left, (list, tuple, str)):
            if augmented and isinstance(left, list):
                cost = len(right)
                left.extend(right)
                return left, cost
            result = ARITHMETIC[op](left, right)
            return result, len(result) if augmented else max(1, len(result))
        return ARITHMETIC[op](*args), 1
    if name == 'compare':
        ops, *values = args
        counter = [0]
        result = True
        for op, left, right in zip(ops, values, values[1:]):
            if op in ('Eq', 'NotEq'):
                result = equals(left, right, counter) == (op == 'Eq')
            elif op in ('In', 'NotIn'):
                result = contains(left, right, counter) == (op == 'In')
            elif op in ('Is', 'IsNot'):
                counter[0] += 1
                result = (left is right) == (op == 'Is')
            else:
                value = compare(left, right, counter)
                result = {'Lt': value < 0, 'LtE': value <= 0,
                          'Gt': value > 0, 'GtE': value >= 0}[op]
            if not result:
                break
        return result, counter[0]
    if name == 'container':
        value, = args
        cost = 1 if isinstance(value, tuple) else 1 + len(value) if isinstance(value, dict) else max(1, size(value)) if isinstance(value, set) else max(1, len(value))
        return value, cost
    if name == 'get':
        collection, index = args
        result = collection[index_value(collection, index)]
        cost = max(1, size(index)) if isinstance(collection, dict) else max(1, len(result)) if isinstance(index, slice) else 1
        return result, cost
    if name == 'set':
        value, collection, index, op = args
        index = index_value(collection, index)
        cost = max(1, size(index)) if isinstance(collection, dict) else 1
        if op:
            value, extra = operation('Aug' + op, collection[index], value)
            cost += extra
        collection[index] = value
        return None, cost
    raise ValueError(f'未知解释器操作：{name}')


def builtin_cost(name, args, result, before):
    """容器修改成本使用修改前长度；构造和查询使用实际返回值。"""
    if name in ('list', 'set', 'dict'):
        return 1 + len(result) * (2 if name == 'dict' else 1)
    if name in ('insert', 'pop') and isinstance(args[0], list):
        index = math.floor(args[1]) if len(args) > 1 else -1
        if index < 0:
            index += before
        return before - index + (1 if name == 'insert' else 0)
    if name in ('add', 'remove', 'pop') and isinstance(args[0], (dict, set)):
        return size(args[1])
    return 1


class Timing(ast.NodeTransformer):
    """在源码树上插入计费点；生成的辅助节点不再递归转换。"""

    def visit(self, node):
        if getattr(node, '_untimed', False):
            return node
        return super().visit(node)

    def __init__(self):
        self.serial = 0

    def temporary(self):
        """使用编译器保留前缀，避免覆盖脚本局部变量。"""
        self.serial += 1
        return f'_timing_{self.serial}'

    @staticmethod
    def call(name, args):
        """构造内部生成器调用，不经过用户函数调用计费。"""
        return ast.YieldFrom(ast.Call(ast.Name(name, ast.Load()), args, []))

    def elapsed(self, value, ticks=1):
        """在求值后结算固定成本，再把同一值交回控制流。"""
        return self.call('_elapsed', [value, ast.Constant(ticks) if isinstance(ticks, int) else ticks])

    def op(self, name, *args):
        """由运行时根据操作数类型计算成本。"""
        return self.call('_operation', [ast.Constant(name), *args])

    def visit_BinOp(self, node):
        self.generic_visit(node)
        return ast.copy_location(self.op(type(node.op).__name__, node.left, node.right), node)

    def visit_Compare(self, node):
        self.generic_visit(node)
        ops = ast.Tuple([ast.Constant(type(op).__name__) for op in node.ops], ast.Load())
        return ast.copy_location(self.op('compare', ops, node.left, *node.comparators), node)

    def visit_BoolOp(self, node):
        """保留短路，并在选中的右值求值后收取每个布尔操作的1t。"""
        self.generic_visit(node)
        result = node.values[0]
        for right in node.values[1:]:
            name = self.temporary()
            condition = ast.NamedExpr(ast.Name(name, ast.Store()), result)
            left = ast.Name(name, ast.Load())
            yes, no = (right, left) if isinstance(node.op, ast.And) else (left, right)
            result = self.elapsed(ast.IfExp(condition, yes, no))
        return ast.copy_location(result, node)

    def visit_If(self, node):
        self.generic_visit(node)
        node.test = self.elapsed(node.test)
        return node

    def visit_While(self, node):
        """while仅在首次判定后收取分支成本；循环体中的操作另行计费。"""
        self.generic_visit(node)
        name = self.temporary()
        node.test = self.elapsed(node.test, ast.Name(name, ast.Load()))
        node.body.insert(0, ast.Assign([ast.Name(name, ast.Store())], ast.Constant(0)))
        return [ast.copy_location(ast.Assign([ast.Name(name, ast.Store())], ast.Constant(1)), node), node]

    def visit_For(self, node):
        target = node.target
        node.target = ast.Name(self.temporary(), ast.Store())
        self.generic_visit(node)
        assignment = self.store(target, ast.Name(node.target.id, ast.Load()))
        node.body[:0] = assignment if isinstance(assignment, list) else [assignment]
        node.iter = self.elapsed(node.iter)
        return node

    def visit_Pass(self, node):
        return ast.copy_location(ast.Expr(self.elapsed(ast.Constant(None))), node)

    def visit_FunctionDef(self, node):
        """原版默认参数在调用时求值，不共享定义时创建的可变容器。"""
        defaults = list(zip(node.args.args[-len(node.args.defaults):], node.args.defaults)) if node.args.defaults else []
        node.args.defaults = []
        self.generic_visit(node)
        initializers = []
        for parameter, value in defaults:
            initializers.append(ast.If(
                ast.Compare(ast.Name(parameter.arg, ast.Load()), [ast.Is()], [ast.Name('_missing', ast.Load())]),
                [ast.Assign([ast.Name(parameter.arg, ast.Store())], self.visit(value))], []))
            node.args.defaults.append(ast.Name('_missing', ast.Load()))
        node.body[:0] = initializers
        return [node, ast.copy_location(ast.Expr(self.elapsed(ast.Constant(None))), node)]

    def visit_List(self, node):
        self.generic_visit(node)
        if isinstance(node.ctx, ast.Store):
            return node
        return ast.copy_location(self.op('container', node), node)

    visit_Tuple = visit_List

    def visit_Dict(self, node):
        self.generic_visit(node)
        return ast.copy_location(self.op('container', node), node)

    visit_Set = visit_Dict

    def index(self, node):
        """将切片AST转换为内部slice值；辅助调用不计费。"""
        if isinstance(node, ast.Slice):
            return ast.Call(ast.Name('_slice', ast.Load()),
                            [self.visit(v) if v is not None else ast.Constant(None)
                             for v in (node.lower, node.upper, node.step)], [])
        return self.visit(node)

    def visit_Subscript(self, node):
        if isinstance(node.ctx, ast.Store):
            return node
        return ast.copy_location(self.op('get', self.visit(node.value), self.index(node.slice)), node)

    def store(self, target, value, op=''):
        """下标写入先算右值，再算目标；目标表达式只求值一次。"""
        if isinstance(target, ast.Subscript):
            return ast.Expr(self.op('set', value, self.visit(target.value), self.index(target.slice), ast.Constant(op)))
        if isinstance(target, (ast.Tuple, ast.List)):
            names = [self.temporary() for _ in target.elts]
            unpack = ast.Tuple([ast.Name(name, ast.Store()) for name in names], ast.Store())
            result = [ast.Assign([unpack], value)]
            for part, name in zip(target.elts, names):
                statement = self.store(part, ast.Name(name, ast.Load()))
                result.extend(statement if isinstance(statement, list) else [statement])
            return result
        if op:
            name = self.temporary()
            return [ast.Assign([ast.Name(name, ast.Store())], value),
                    ast.Assign([target], self.op('Aug' + op, ast.Name(target.id, ast.Load()), ast.Name(name, ast.Load())))]
        return ast.Assign([target], value)

    def visit_Assign(self, node):
        value = self.visit(node.value)
        if len(node.targets) == 1:
            result = self.store(node.targets[0], value)
            return [ast.copy_location(part, node) for part in result] if isinstance(result, list) else ast.copy_location(result, node)
        name = self.temporary()
        result = [ast.Assign([ast.Name(name, ast.Store())], value)]
        for target in node.targets:
            statement = self.store(target, ast.Name(name, ast.Load()))
            result.extend(statement if isinstance(statement, list) else [statement])
        return [ast.copy_location(part, node) for part in result]

    def visit_AugAssign(self, node):
        result = self.store(node.target, self.visit(node.value), type(node.op).__name__)
        return [ast.copy_location(part, node) for part in result] if isinstance(result, list) else ast.copy_location(result, node)


class StaticBindings(ast.NodeTransformer):
    """跟踪每个词法绑定的静态标记；别名和重新赋值不继承函数定义的免费调用。"""

    def __init__(self):
        self.scopes = []
        self.serial = 0
        self.conditional = 0

    @staticmethod
    def native(node):
        """编译器状态不属于游戏操作，不交给Timing再次计费。"""
        node._untimed = True
        return node

    def enter(self, node, parameters=()):
        """只收集当前作用域的绑定；子函数通过独立字典保存标记。"""
        names: set[str] = set(parameters)
        globals_: set[str] = set()

        class Names(ast.NodeVisitor):
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Store):
                    names.add(node.id)

            def visit_FunctionDef(self, node):
                names.add(node.name)

            def visit_Global(self, node):
                globals_.update(node.names)

        for statement in node.body:
            Names().visit(statement)
        if not self.scopes:
            for child in ast.walk(node):
                if isinstance(child, ast.Global):
                    names.update(child.names)
        names.difference_update(globals_)
        self.serial += 1
        scope = (names, globals_, f'_timing_bindings_{self.serial}')
        self.scopes.append(scope)
        return self.native(ast.Assign([ast.Name(scope[2], ast.Store())],
            ast.Dict([ast.Constant(name) for name in sorted(names)],
                     [ast.Constant(False) for _ in names])))

    def flag(self, name, context):
        """global使用模块字典，其他名称按最近词法作用域解析。"""
        scopes = self.scopes[:1] if name in self.scopes[-1][1] else self.scopes
        for names, _, variable in reversed(scopes):
            if name in names:
                return ast.Subscript(ast.Name(variable, ast.Load()), ast.Constant(name), context)
        return ast.Constant(False)

    def set_flag(self, name, value):
        return self.native(ast.Assign([self.flag(name, ast.Store())], ast.Constant(value)))

    def invalidate(self, targets):
        """仅名称绑定失去静态性；下标写入不改变容器变量的绑定。"""
        result = []
        for target in targets:
            if isinstance(target, ast.Name):
                result.append(self.set_flag(target.id, False))
            elif isinstance(target, (ast.Tuple, ast.List)):
                result.extend(self.invalidate(target.elts))
        return result

    def visit_Module(self, node):
        initial = self.enter(node)
        self.generic_visit(node)
        node.body.insert(0, initial)
        self.scopes.pop()
        return node

    def visit_FunctionDef(self, node):
        flag = self.set_flag(node.name, self.conditional == 0)
        conditional = self.conditional
        self.conditional = 0
        initial = self.enter(node, (arg.arg for arg in node.args.args))
        self.generic_visit(node)
        node.body.insert(0, initial)
        self.scopes.pop()
        self.conditional = conditional
        return [node, flag]

    def visit_Call(self, node):
        self.generic_visit(node)
        node._static_flag = self.flag(node.func.id, ast.Load()) if isinstance(node.func, ast.Name) else ast.Constant(False)
        return node

    def visit_Assign(self, node):
        self.generic_visit(node)
        return [node, *self.invalidate(node.targets)]

    def visit_AugAssign(self, node):
        self.generic_visit(node)
        return [node, *self.invalidate([node.target])]

    def visit_For(self, node):
        self.conditional += 1
        self.generic_visit(node)
        self.conditional -= 1
        node.body[:0] = self.invalidate([node.target])
        return node

    def visit_If(self, node):
        self.conditional += 1
        self.generic_visit(node)
        self.conditional -= 1
        return node

    visit_While = visit_If
