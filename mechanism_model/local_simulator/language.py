"""游戏容器函数；保留原版索引边界，不直接借用 Python 的截断插入语义。"""

import math
from enum import Enum


def game_str(value=''):
    """输出游戏枚举和容器表示；不包含完整原版浮点格式化器。"""
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (list, tuple, set)):
        left, right = ('[', ']') if isinstance(value, list) else ('(', ')') if isinstance(value, tuple) else ('{', '}')
        return left + ','.join(game_str(v) for v in value) + right
    if isinstance(value, dict):
        return '{' + ','.join(game_str(k) + ':' + game_str(v) for k, v in value.items()) + '}'
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def append(values, value):
    if not isinstance(values, list):
        raise TypeError('append 需要列表')
    values.append(value)


def add(values, value):
    if not isinstance(values, set):
        raise TypeError('add 需要集合')
    values.add(value)


def insert(values, index, value):
    if not isinstance(values, list):
        raise TypeError('insert 需要列表')
    index = math.floor(index)
    if index < 0:
        index += len(values)
    if not 0 <= index <= len(values):
        raise IndexError('insert 索引超出列表边界')
    values.insert(index, value)


def pop(values, *indices):
    if len(indices) > 1:
        raise TypeError('pop 最多接受一个索引')
    if isinstance(values, list):
        return values.pop(math.floor(indices[0]) if indices else -1)
    if isinstance(values, dict) and indices:
        return values.pop(indices[0])
    raise TypeError('pop 需要列表，或字典和键')


def remove(values, value):
    if not isinstance(values, (list, set)):
        raise TypeError('remove 需要列表或集合')
    values.remove(value)


BUILTINS = {'range': range, 'min': min, 'max': max, 'len': len, 'abs': abs,
            'str': game_str, 'list': list, 'dict': dict, 'set': set,
            'append': append, 'insert': insert, 'pop': pop, 'remove': remove, 'add': add}
