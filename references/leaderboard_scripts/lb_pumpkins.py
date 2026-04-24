from __builtins__ import *


PUMPKIN_GOAL = 200000000


# main3: 旧 27x27 / 16 块 6x6 并行基线，结论保留在 md。
# main4: 16x16 混合布局，两个 8x8 + 两个 6x6，每片 2 机分半区。
def main4():
    set_world_size(16)

    spawn_block(0, 0, 8)
    spawn_block(8, 8, 8)
    spawn_block(10, 0, 6)
    goto(0, 10)
    main4_block_worker(0, 10, 6)


def spawn_block(x0, y0, size):
    goto(x0, y0)
    spawn_drone(main4_corner_worker)
    goto(x0, y0)
    spawn_drone(main4_block_worker, x0, y0, size)


def main4_corner_worker():
    # 角 watcher 暂时只占位，避免未来需要通信时再重构 spawn 布局。
    while num_items(Items.Pumpkin) < PUMPKIN_GOAL:
        do_a_flip()


def main4_block_worker(x0, y0, size):
    while num_items(Items.Pumpkin) < PUMPKIN_GOAL:
        plant_area(x0, y0, size, 0, size)
        wait_block_by_corners(x0, y0, size)
        harvest_block(x0, y0)


def wait_block_by_corners(x0, y0, size):
    while True:
        goto(x0, y0)
        a = measure()
        goto((x0 + size - 1) % get_world_size(), (y0 + size - 1) % get_world_size())
        b = measure()
        if a == b:
            return
        scan_area(x0, y0, size, 0, size, 1)

def run_slice(x0, y0, width, y_offset, height):
    while num_items(Items.Pumpkin) < PUMPKIN_GOAL:
        plant_area(x0, y0, width, y_offset, height)
        wait_area(x0, y0, width, y_offset, height)
        harvest_area(x0, y0, width, y_offset, height)


def plant_area(x0, y0, width, y_offset, height):
    scan_area(x0, y0, width, y_offset, height, 0)


def wait_area(x0, y0, width, y_offset, height):
    while True:
        pending = scan_area(x0, y0, width, y_offset, height, 1)
        if pending == 0:
            return


def harvest_area(x0, y0, width, y_offset, height):
    scan_area(x0, y0, width, y_offset, height, 2)


def harvest_block(x0, y0):
    # 角测确认整块合并后，任意一格收割即可结算整个 giant pumpkin。
    goto(x0, y0)
    if get_entity_type() == Entities.Pumpkin and can_harvest():
        harvest()


def scan_area(x0, y0, width, y_offset, height, mode):
    pending = 0
    goto(x0, y0 + y_offset)
    for local_y in range(height):
        if local_y % 2 == 0:
            move_dir = East
            end_dx = width - 1
            step = 1
        else:
            move_dir = West
            end_dx = 0
            step = -1

        dx = (get_pos_x() - x0) % get_world_size()
        while True:
            entity = get_entity_type()
            if mode == 2:
                if entity == Entities.Pumpkin and can_harvest():
                    harvest()
            elif entity == Entities.Pumpkin:
                if not can_harvest():
                    pending = pending + 1
                    water_pumpkin()
            else:
                if entity != None and entity != Entities.Dead_Pumpkin:
                    harvest()
                if get_ground_type() != Grounds.Soil:
                    till()
                plant(Entities.Pumpkin)
                pending = pending + 1
                water_pumpkin()

            if dx == end_dx:
                break
            move(move_dir)
            dx = dx + step

        if local_y < height - 1:
            move(North)
    return pending


def water_pumpkin():
    if get_water() < 0.5 and num_items(Items.Water) > 5:
        use_item(Items.Water)


def goto(tx, ty):
    size = get_world_size()
    half = size // 2
    x = get_pos_x()
    y = get_pos_y()

    dx = (tx - x) % size
    if dx <= half:
        for _ in range(dx):
            move(East)
    else:
        for _ in range(size - dx):
            move(West)

    dy = (ty - y) % size
    if dy <= half:
        for _ in range(dy):
            move(North)
    else:
        for _ in range(size - dy):
            move(South)


if __name__ == "__main__":
    main4()
