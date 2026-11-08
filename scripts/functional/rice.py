from __builtins__ import *
import production


# 来源lb_rice.py：两层粘土流水，成功收割后再下挖；只在全部工人回收后换田。
def rice(target=-1):
    size = get_world_size()
    workers = min(size, max_drones())
    batch = 0
    while production.active(Items.Rice, target):
        deadline = get_time() + 3600
        clear()
        handles = []
        local = True
        for column in range(1, workers):
            handle = spawn_drone(rice_columns, column, workers, size, deadline, target)
            if handle == None:
                local = False
                break
            handles.append(handle)
        if not rice_columns(0, workers, size, deadline, target):
            local = False
        for handle in handles:
            if not wait_for(handle):
                local = False
        quick_print("rice_batch", batch, local, get_time(), num_items(Items.Rice))
        if not local:
            quick_print("rice_failed", "batch", batch)
            return
        batch += 1


def rice_columns(first, stride, size, deadline, target):
    planted = []
    for x in range(first, size, stride):
        if not rice_move_to(x, 0, size):
            return False
        for y in range(size):
            if not production.active(Items.Rice, target):
                return True
            ground = get_ground_type()
            digs = 0
            while ground != Grounds.Clay and ground != Grounds.Rock and digs < 128:
                if get_time() > deadline or not dig():
                    return False
                ground = get_ground_type()
                digs += 1
            if ground == Grounds.Clay:
                if not plant(Entities.Rice):
                    return False
                if get_water() < 0.25 and num_items(Items.Water) > 0:
                    use_item(Items.Water)
                planted.append((x, y))
            if not move(North):
                return False
    second = []
    for x, y in planted:
        if not production.active(Items.Rice, target):
            return True
        if not rice_move_to(x, y, size):
            return False
        while get_entity_type() == Entities.Rice and not can_harvest():
            if get_time() > deadline:
                return False
            do_a_flip()
        if get_entity_type() == Entities.Rice:
            if not harvest():
                return False
            if production.active(Items.Rice, target) and get_ground_type() == Grounds.Dry_Rice_Terrace:
                if get_time() > deadline or not dig():
                    return False
                if get_ground_type() == Grounds.Clay:
                    if not plant(Entities.Rice):
                        return False
                    if get_water() < 0.25 and num_items(Items.Water) > 0:
                        use_item(Items.Water)
                    second.append((x, y))
    for x, y in second:
        if not production.active(Items.Rice, target):
            return True
        if not rice_move_to(x, y, size):
            return False
        while get_entity_type() == Entities.Rice and not can_harvest():
            if get_time() > deadline:
                return False
            do_a_flip()
        if get_entity_type() == Entities.Rice and not harvest():
            return False
    return True


def rice_move_to(tx, ty, size):
    dx = (tx - get_pos_x()) % size
    direction = East
    if dx > size // 2:
        direction = West
        dx = size - dx
    for _ in range(dx):
        if not move(direction):
            return False
    dy = (ty - get_pos_y()) % size
    direction = North
    if dy > size // 2:
        direction = South
        dy = size - dy
    for _ in range(dy):
        if not move(direction):
            return False
    return True


if __name__ == "__main__":
    rice()
