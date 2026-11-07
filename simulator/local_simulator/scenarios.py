"""由游戏资产展开地下排行榜初始库存、科技、目标和专用地形参数。"""
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
