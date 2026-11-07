"""解析脚本初始科技、存档库存，以及由游戏资产展开的地下排行榜场景。"""
import math
from .catalog import Items, UNDERGROUND, UNLOCK_DATA


RESET_UNLOCKS = ('loops', 'debug', 'debug_2', 'timing', 'lists', 'dictionaries', 'costs',
                 'auto_unlock', 'operators', 'variables', 'senses', 'utilities', 'functions',
                 'import', 'simulation', 'underground_senses')


def leaderboard_scenario(scenario):
    """排行榜参数允许显式库存/科技/目标覆盖，报告保留原始场景供复核。"""
    name = scenario.get('leaderboard')
    if name is None:
        return scenario, None
    if not isinstance(name, str):
        raise ValueError('leaderboard 需要地下排行榜名称')
    key = name.removeprefix('Leaderboards.').removeprefix('lb_').title()
    if key not in UNDERGROUND['leaderboards']:
        raise ValueError(f'未知地下排行榜：{name}')
    profile = UNDERGROUND['leaderboards'][key]
    unlocked = ({key: row['max_unlock_level'] for key, row in UNLOCK_DATA.items()}
                if profile['everythingUnlocked'] else dict.fromkeys(RESET_UNLOCKS, 1) | {'grass': 1})
    if profile['singleDrone']:
        unlocked.update(megafarm=0, expand=5)
    unlocked.update(scenario.get('unlocks', {}))
    items = dict.fromkeys((item.name for item in Items), 0) | profile['items']
    items.update(scenario.get('items', {}))
    normalized = dict(scenario, preset='reset', unlocks=unlocked, items=items)
    if 'goal' not in scenario:
        if profile['goal_items']:
            item, amount = next(iter(profile['goal_items'].items()))
            normalized['goal'] = {'item': item, 'amount': amount}
        else:
            normalized['goal'] = {'unlock': 'Underground_Leaderboard'}
    return normalized, profile


def unlock_overrides(values):
    """解析CLI的科技=等级，使用与场景相同的科技名和范围。"""
    result = {}
    for value in values:
        name, separator, text = value.partition('=')
        key = name.removeprefix('Unlocks.').lower()
        if not separator or key not in UNLOCK_DATA:
            raise ValueError(f'无效科技覆盖 {value!r}；请使用 科技名=整数等级')
        try:
            level = int(text)
        except ValueError as exc:
            raise ValueError(f'科技等级必须是整数：{value}') from exc
        maximum = UNLOCK_DATA[key]['max_unlock_level']
        if not 0 <= level <= maximum:
            raise ValueError(f'{name} 等级范围为0..{maximum}：{level}')
        if key in result:
            raise ValueError(f'科技重复设置：{name}')
        result[key] = level
    return result


def save_scenario(data):
    """只导入Save0 JSON的科技和库存；地形和运行状态仍由seed生成。"""
    if not isinstance(data, dict) or not isinstance(data.get('unlocks'), list):
        raise ValueError('存档JSON需要unlocks列表')
    unlocks = dict.fromkeys(UNLOCK_DATA, 0)
    for symbol in data['unlocks']:
        if not isinstance(symbol, str):
            raise ValueError('存档unlocks条目必须是字符串')
        key, separator, suffix = symbol.rpartition('_')
        if symbol in UNLOCK_DATA:
            # debug_2是独立科技，必须先匹配全名再解析等级后缀。
            key, level = symbol, 1
        elif separator and suffix.isdigit():
            level = int(suffix)
        else:
            key, level = symbol, 1
        if key in UNLOCK_DATA:
            if not 0 <= level <= UNLOCK_DATA[key]['max_unlock_level']:
                raise ValueError(f'存档科技等级超出模型范围：{symbol}')
            unlocks[key] = max(unlocks[key], level)
    rows = data.get('items', {}).get('serializeList') if isinstance(data.get('items'), dict) else None
    if not isinstance(rows, list):
        raise ValueError('存档JSON需要items.serializeList列表')
    names = {item.name.lower(): item.name for item in Items}
    items = {}
    for row in rows:
        if not isinstance(row, dict) or row.get('name') not in names:
            raise ValueError(f'未知存档物品：{row!r}')
        name, amount = names[row['name']], row.get('nr')
        if name in items or type(amount) not in (int, float) or not math.isfinite(amount) or amount < 0:
            raise ValueError(f'无效或重复存档库存：{row!r}')
        items[name] = amount
    return {'preset': 'reset', 'unlocks': unlocks, 'items': items}
