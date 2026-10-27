"""游戏容器函数；保留原版索引边界，不直接借用 Python 的截断插入语义。"""

import math
from enum import Enum


def game_len(value):
    """字符串长度使用游戏的UTF-16代码单元；容器仍按元素计数。"""
    return len(value.encode('utf-16-le', 'surrogatepass')) // 2 if isinstance(value, str) else len(value)


def string_units(value):
    """按.NET char拆分字符串，保留代理项以供索引和切片。"""
    encoded = value.encode('utf-16-le', 'surrogatepass')
    return [encoded[i:i + 2].decode('utf-16-le', 'surrogatepass') for i in range(0, len(encoded), 2)]


def game_iter(value):
    return string_units(value) if isinstance(value, str) else value


def game_list(value=()):
    return list(game_iter(value))


def game_set(value=()):
    return set(game_iter(value))


def join_units(values):
    return ''.join(values).encode('utf-16-le', 'surrogatepass').decode('utf-16-le', 'surrogatepass')


def game_str(value='', depth=0, seen=None, sequence_element=False):
    """容器字符串遵循ToNiceString的引号、重复引用及深度规则。"""
    if depth > 100:
        return ''
    if seen is not None and id(value) in seen:
        return '...'
    if isinstance(value, (list, dict)):
        if seen is None:
            seen = set()
        seen.add(id(value))
    def nested(item):
        return game_str(item, depth + 1, seen, True)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (list, tuple, set)):
        left, right = ('[', ']') if isinstance(value, list) else ('(', ')') if isinstance(value, tuple) else ('{', '}')
        return left + ','.join(nested(v) for v in value) + right
    if isinstance(value, dict):
        return '{' + ','.join(nested(k) + ':' + nested(v) for k, v in value.items()) + '}'
    if isinstance(value, str) and sequence_element:
        return "'" + value + "'"
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


BUILTINS = {'range': range, 'min': min, 'max': max, 'len': game_len, 'abs': abs,
            'str': game_str, 'list': game_list, 'dict': dict, 'set': game_set,
            'append': append, 'insert': insert, 'pop': pop, 'remove': remove, 'add': add}
