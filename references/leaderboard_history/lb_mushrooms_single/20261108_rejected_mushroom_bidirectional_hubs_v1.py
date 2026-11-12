from __builtins__ import *
# 淘汰候选归档：lb_mushrooms_single | 原实验路径 .codex/nonreset-100-20261108/mushroom-bidirectional-hubs-v1/lb_mushrooms_single.py

def lb_mushrooms_single():
    began = get_time()
    size = get_world_size()
    centers = []
    for y in range(size):
        for x in range(size):
            if (x + 2 * y) % 5 == 0:
                centers.append((x, y))
    for batch in range(128):
        if num_items(Items.Mushroom) >= 30000:
            quick_print("mushrooms_done", True, get_time(), num_items(Items.Mushroom))
            return
        clear()
        for step in range(256):
            if get_ground_type() == Grounds.Mushroom:
                break
            if get_time() - began > 7200 or not dig():
                quick_print("mushrooms_failed", "find", batch)
                return
        if get_ground_type() != Grounds.Mushroom:
            quick_print("mushrooms_failed", "find_limit", batch)
            return
        top = get_pos_z()
        if not dig_layer(top):
            quick_print("mushrooms_failed", "cover", batch)
            return
        for x, y in centers:
            if num_items(Items.Mushroom) >= 30000:
                break
            if not work_star(x, y, size):
                quick_print("mushrooms_failed", "star", batch, x, y)
                return
        quick_print("mushrooms_batch", batch, get_time(), num_items(Items.Mushroom))
    quick_print("mushrooms_failed", "batch_limit", get_time(), num_items(Items.Mushroom))


def work_star(x, y, size):
    if not move_to(x, y):
        return False
    neighbors = []
    if y + 1 < size:
        neighbors.append(0)
    if x + 1 < size:
        neighbors.append(1)
    if y > 0:
        neighbors.append(2)
    if x > 0:
        neighbors.append(3)
    previous_out = -1
    previous_in = -1
    rotor = 0
    dry = 0
    for turn in range(128):
        if num_items(Items.Mushroom) >= 30000:
            return True
        center_z = get_pos_z()
        center_color = -1
        if get_ground_type() == Grounds.Mushroom:
            center_color = measure()
        heights = [0, 0, 0, 0]
        colors = [-1, -1, -1, -1]
        outgoing = -1
        incoming = -1
        live = 0
        for i in neighbors:
            direction = DIRECTIONS[i]
            heights[i] = get_pos_z(direction)
            if get_ground_type(direction) == Grounds.Mushroom:
                colors[i] = measure(direction)
                live += 1
                if colors[i] == center_color:
                    if center_z > heights[i]:
                        outgoing = i
                    elif heights[i] > center_z:
                        incoming = i
        if outgoing >= 0:
            if not push(DIRECTIONS[outgoing]):
                return False
            previous_out = outgoing
            previous_in = -1
            dry = 0
            continue
        if incoming >= 0:
            if not push_neighbor(incoming):
                return False
            previous_out = -1
            previous_in = incoming
            dry = 0
            continue
        if live == 0 and center_color < 0:
            return True
        if dry >= 20:
            return True
        outgoing = -1
        incoming = -1
        for offset in range(4):
            i = (rotor + offset) % 4
            if i not in neighbors:
                continue
            if center_color >= 0 and heights[i] < center_z and i != previous_in:
                outgoing = i
                break
            if colors[i] >= 0 and heights[i] > center_z and i != previous_out:
                incoming = i
        rotor = (rotor + 1) % 4
        if outgoing >= 0:
            if not push(DIRECTIONS[outgoing]):
                return False
            previous_out = outgoing
            previous_in = -1
        elif incoming >= 0:
            if not push_neighbor(incoming):
                return False
            previous_out = -1
            previous_in = incoming
        else:
            # 反向撤销不能算新动作；只有实际没有可推边才开启动空位。
            movable = False
            for i in neighbors:
                if center_color >= 0 and heights[i] < center_z or colors[i] >= 0 and heights[i] > center_z:
                    movable = True
                    break
            if movable:
                return True
            if get_hardness() >= 10000000 or not dig():
                return False
            previous_out = -1
            previous_in = -1
        dry += 1
    return True


# 每台无人机负责一列；无人机不足时按列步长分担，整层完成后才返回。
def dig_layer(target):
    size = get_world_size()
    workers = min(size, max_drones())
    handles = []
    ok = True
    for x in range(workers - 1):
        if not move_to(x, 0):
            ok = False
            break
        handle = spawn_drone(dig_columns, x, workers, size, target)
        if handle == None:
            if not dig_columns(x, workers, size, target):
                ok = False
        else:
            handles.append(handle)
    if ok and not dig_columns(workers - 1, workers, size, target):
        ok = False
    for handle in handles:
        if not wait_for(handle):
            ok = False
    return ok


# 覆盖层起始高度一致，只需逐格挖到本次目标高度，无需识别地面类型。
def dig_columns(first_x, stride, size, target):
    for x in range(first_x, size, stride):
        if not move_to(x, 0):
            return False
        for y in range(size):
            while get_pos_z() > target:
                if not dig():
                    return False
            if get_pos_z() != target:
                return False
            if not move(North):
                return False
    return True


def move_to(tx, ty):
    size = get_world_size()
    dx = (tx - get_pos_x()) % size
    dy = (ty - get_pos_y()) % size
    horizontal = East
    vertical = North
    if dx > size // 2:
        dx = size - dx
        horizontal = West
    if dy > size // 2:
        dy = size - dy
        vertical = South
    for _ in range(dx):
        if not move(horizontal):
            return False
    for _ in range(dy):
        if not move(vertical):
            return False
    return True


def push_neighbor(i):
    if not move(DIRECTIONS[i]):
        return False
    pushed = push(BACKS[i])
    if not move(BACKS[i]):
        return False
    return pushed


DIRECTIONS = [North, East, South, West]
BACKS = [South, West, North, East]


if __name__ == "__main__":
    lb_mushrooms_single()
