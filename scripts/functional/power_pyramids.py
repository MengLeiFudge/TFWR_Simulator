from __builtins__ import *
import farm_support


def power_pyramids():
    # 同一时间只修一座塔，全部补缺后由中心主机补塔尖并收取能量。
    farm_support.run(Items.Power, collect)


def collect(goal):
    # 普通地形按公开沙面和石灰岩定位，不采用排行榜专用的16层深度。
    if not farm_support.require(Unlocks.Pyramid) or not farm_support.require(Unlocks.Mining):
        return False
    if not farm_support.require(Unlocks.Underground_Senses):
        return False
    width, size = farm_support.dimensions()
    if min(width, size) < 5:
        quick_print("金字塔需要至少5×5的农场。")
        return False
    empty = 0
    reserve = width * size
    while num_items(Items.Power) < goal:
        if not farm_support.stock(Items.Block, reserve):
            return False
        clear()
        point = find_floor()
        if point == None:
            empty += 1
            if empty >= 8:
                quick_print("连续八片未找到可修复金字塔，停止。")
                return False
            continue
        x, y, floor = point
        bounds = find_bounds(x, y, floor)
        if bounds == None:
            return False
        holes = prepare(bounds)
        if holes == None:
            return False
        needed = 1
        for x, y, z, target in holes:
            needed += target - z
        if num_items(Items.Block) < needed:
            # 补料会清场，当前塔不再继续；按已知缺口提高下一片的预留量。
            reserve = needed
            continue
        if not repair(holes, bounds):
            return False
        empty = 0
    return True


def find_floor():
    # 间隔4格的探孔会穿过任意边长至少5的足印；先沿沙面找外缘，再下到基座。
    width, size = farm_support.dimensions()
    for x in range(0, width, 4):
        for y in range(0, size, 4):
            if not farm_support.move_to(x, y):
                return None
            for _ in range(256):
                ground = get_ground_type()
                if ground == Grounds.Sand or ground == Grounds.Limestone:
                    break
                if get_hardness() >= 10000000 or not dig():
                    break
            if get_ground_type() != Grounds.Sand and get_ground_type() != Grounds.Limestone:
                continue
            while get_ground_type() == Grounds.Sand and get_pos_x() > 0:
                previous = get_pos_x()
                limit = get_pos_z() - 1
                if not move(West):
                    return None
                while get_pos_z() > limit:
                    ground = get_ground_type()
                    if ground == Grounds.Sand or ground == Grounds.Limestone:
                        break
                    if not dig():
                        return None
                ground = get_ground_type()
                if ground != Grounds.Sand and ground != Grounds.Limestone:
                    if not farm_support.move_to(previous, get_pos_y()):
                        return None
                    break
            for _ in range(32):
                if get_ground_type() == Grounds.Limestone:
                    return get_pos_x(), get_pos_y(), get_pos_z()
                if get_hardness() >= 10000000 or not dig():
                    return None
    return None


def inside(x, y, floor):
    # 找边仅清除覆盖物，遇沙停止，禁止挖穿基座。
    if not farm_support.move_to(x, y):
        return False
    while get_pos_z() > floor:
        if get_ground_type() == Grounds.Sand:
            return True
        if get_hardness() >= 10000000 or not dig():
            return False
    return get_pos_z() == floor and get_ground_type() == Grounds.Limestone


def find_bounds(x, y, floor):
    # 从塔内一点测四条边，正方形足印足以确定所有位置的目标高度。
    width, size = farm_support.dimensions()
    edges = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        px = x
        py = y
        while True:
            nx = px + dx
            ny = py + dy
            if nx < 0 or nx >= width or ny < 0 or ny >= size or not inside(nx, ny, floor):
                break
            px = nx
            py = ny
        edges.append((px, py))
    x0 = edges[0][0]
    x1 = edges[1][0]
    y0 = edges[2][1]
    y1 = edges[3][1]
    length = x1 - x0 + 1
    if length < 5 or length % 2 == 0 or y1 - y0 + 1 != length:
        quick_print("金字塔边界不符合正方形，停止。")
        return None
    return x0, x1, y0, y1, floor


def prepare(bounds):
    # 完成全塔清土后记录缺口，留中心顶块作为完成锁。
    x0, x1, y0, y1, floor = bounds
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2
    height = (x1 - x0 + 2) // 2
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            if not farm_support.move_to(x, y):
                return None
            while get_pos_z() > floor:
                ground = get_ground_type()
                if ground == Grounds.Sand or ground == Grounds.Limestone:
                    break
                if not dig():
                    return None
            if get_pos_z() < floor:
                return None
    if not farm_support.move_to(cx, cy):
        return None
    if get_pos_z() == floor + height:
        if not dig():
            return None
    holes = []
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            if not farm_support.move_to(x, y):
                return None
            target = floor + 1 + min(x - x0, x1 - x, y - y0, y1 - y)
            if x == cx and y == cy:
                target -= 1
            z = get_pos_z()
            if z < floor or z > target:
                return None
            if z < target:
                holes.append((x, y, z, target))
    return holes


def repair(holes, bounds):
    # 底层完整后再放高层，避免沙塌；最后一次放块只在中心进行。
    x0, x1, y0, y1, floor = bounds
    height = (x1 - x0 + 2) // 2
    for layer in range(1, height):
        target = floor + layer
        for x, y, z, top in holes:
            if z >= target or top < target:
                continue
            if not farm_support.move_to(x, y) or get_pos_z() != target - 1:
                return False
            if not place(Grounds.Sand) or get_pos_z() != target:
                return False
    if not farm_support.move_to((x0 + x1) // 2, (y0 + y1) // 2):
        return False
    if get_pos_z() != floor + height - 1 or not place(Grounds.Sand):
        return False
    return get_entity_type() == Entities.Sunflower and harvest()


if __name__ == "__main__":
    power_pyramids()
