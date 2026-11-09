from __builtins__ import *
# 一次性彩色金字塔成就：6×6农场生成5×5天然塔，拆至原基座后重建35块。

WORLD_SIZE = 6
PYRAMID_SIZE = 5
BLOCKS_NEEDED = 35
MAX_ATTEMPTS = 16
MAX_DEPTH = 128
MAX_GAME_SECONDS = 600
COLORS = [Grounds.Red_Block, Grounds.Green_Block, Grounds.Blue_Block]


# 独立启动时清场；只使用一次Jump，复原并收获一座彩色塔后返回。
def power_pyramids_color():
    set_world_size(WORLD_SIZE)
    clear()
    change_hat(Hats.Mining_Hat)
    jump(Unlocks.Pyramid)
    deadline = get_time() + MAX_GAME_SECONDS
    for attempt in range(MAX_ATTEMPTS):
        if attempt > 0:
            clear()
            change_hat(Hats.Mining_Hat)
        quick_print("寻找最小金字塔：第", attempt + 1, "片")
        # 5×5塔在6×6田内只有四种平移，中心(3,3)始终位于足印内。
        if not color_move_to(WORLD_SIZE // 2, WORLD_SIZE // 2):
            return False
        while get_ground_type() != Grounds.Limestone and get_pos_z() > -MAX_DEPTH:
            if get_time() > deadline or get_hardness() >= 10000000 or not dig():
                quick_print("金字塔探孔停止：时间、硬度或挖掘失败，z", get_pos_z())
                return False
        if get_ground_type() != Grounds.Limestone:
            quick_print("深度上限内未找到基座，换田：z", get_pos_z())
            continue
        floor = get_pos_z()
        bounds = color_clear_to_floor(floor, deadline)
        if bounds == None:
            return False
        if num_items(Items.Block) < BLOCKS_NEEDED:
            quick_print("彩色重建需要35个Block，当前", num_items(Items.Block))
            return False
        quick_print("原塔已拆净，开始彩色重建：基座z", floor)
        if not color_rebuild(bounds, floor):
            quick_print("彩色重建失败，停止：位置", get_pos_x(), get_pos_y(), get_pos_z())
            return False
        quick_print("彩色金字塔已复原并收获：底边5，共放置35块。")
        return True
    quick_print("已达到找塔次数上限，未完成彩色金字塔。")
    return False


# 全田挖至同一基座高度，保留石灰岩；25个基座必须恰好组成5×5矩形。
def color_clear_to_floor(floor, deadline):
    x0 = WORLD_SIZE
    x1 = -1
    y0 = WORLD_SIZE
    y1 = -1
    count = 0
    for x in range(WORLD_SIZE):
        for offset in range(WORLD_SIZE):
            y = offset
            if x % 2 == 1:
                y = WORLD_SIZE - 1 - offset
            if not color_move_to(x, y):
                return None
            while get_pos_z() > floor:
                if get_time() > deadline or get_hardness() >= 10000000 or not dig():
                    quick_print("拆塔失败：位置", x, y, get_pos_z())
                    return None
            if get_pos_z() != floor:
                quick_print("拆塔越过基座：位置", x, y, get_pos_z(), "应为", floor)
                return None
            if get_ground_type() == Grounds.Limestone:
                count += 1
                x0 = min(x0, x)
                x1 = max(x1, x)
                y0 = min(y0, y)
                y1 = max(y1, y)
    if count != PYRAMID_SIZE * PYRAMID_SIZE or x1 - x0 + 1 != PYRAMID_SIZE or y1 - y0 + 1 != PYRAMID_SIZE:
        quick_print("基座不符合5×5：数量", count, "边界", x0, x1, y0, y1)
        return None
    return x0, x1, y0, y1


# 拆净后只放块，不再挖掘；按25、9、1层重建，顶块最后触发整塔完成判定。
def color_rebuild(bounds, floor):
    x0, x1, y0, y1 = bounds
    height = PYRAMID_SIZE // 2 + 1
    for layer in range(1, height):
        inset = layer - 1
        for x in range(x0 + inset, x1 - inset + 1):
            for y in range(y0 + inset, y1 - inset + 1):
                if not color_move_to(x, y) or get_pos_z() != floor + layer - 1:
                    return False
                color = COLORS[(x - x0 + y - y0 + layer - 1) % len(COLORS)]
                if not place(color) or get_pos_z() != floor + layer:
                    return False
    if not color_move_to((x0 + x1) // 2, (y0 + y1) // 2):
        return False
    if get_pos_z() != floor + height - 1 or not place(COLORS[(height - 1) % len(COLORS)]):
        return False
    # 完成后游戏清除塔体并生成成熟向日葵；不把place成功当作成就已解锁。
    if get_pos_z() != floor or get_entity_type() != Entities.Sunflower or not can_harvest():
        return False
    return harvest()


# 六格田使用环绕短路径；动作失败时保留现场并报告实际坐标。
def color_move_to(tx, ty):
    dx = (tx - get_pos_x()) % WORLD_SIZE
    horizontal = East
    if dx > WORLD_SIZE // 2:
        dx = WORLD_SIZE - dx
        horizontal = West
    dy = (ty - get_pos_y()) % WORLD_SIZE
    vertical = North
    if dy > WORLD_SIZE // 2:
        dy = WORLD_SIZE - dy
        vertical = South
    for _ in range(dx):
        if not move(horizontal):
            quick_print("金字塔移动失败：位置", get_pos_x(), get_pos_y(), "目标", tx, ty)
            return False
    for _ in range(dy):
        if not move(vertical):
            quick_print("金字塔移动失败：位置", get_pos_x(), get_pos_y(), "目标", tx, ty)
            return False
    return True


if __name__ == "__main__":
    power_pyramids_color()
