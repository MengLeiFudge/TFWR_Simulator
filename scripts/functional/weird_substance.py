from __builtins__ import *
import production


def weird_substance(target=-1):
    # 苗圃只清理一次；每轮回收工人后保留未收获的合格伴生树。
    if not production.active(Items.Weird_Substance, target):
        return
    size = get_world_size()
    workers = min(max_drones(), size // 2)
    deadline = get_time() + 700
    while num_items(Items.Fertilizer) < workers:
        if get_time() > deadline:
            quick_print("nursery_failed", "fertilizer_reserve", workers)
            return
        do_a_flip()
    clear()
    while production.active(Items.Weird_Substance, target):
        began = get_time()
        before = num_items(Items.Weird_Substance)
        deadline = began + 60
        handles = []
        results = []
        ok = True
        for worker in range(1, workers):
            handle = spawn_drone(nursery_produce_strip, worker, workers, size, target, deadline)
            if handle == None:
                ok = False
                break
            handles.append(handle)
        if ok:
            results.append(nursery_produce_strip(0, workers, size, target, deadline))
        for handle in handles:
            results.append(wait_for(handle))
        for result in results:
            if not result:
                ok = False
        quick_print("nursery_cycle", ok, began, get_time(), num_items(Items.Weird_Substance) - before)
        if not ok:
            return


def nursery_produce_strip(worker, workers, size, target, deadline):
    # 偶数坐标独占树位，其余格保留自然Grass；重派后从真实树和伴生关系恢复。
    anchors = []
    for y in range(0, size, 2):
        if (y // 2) % workers == worker:
            for x in range(0, size, 2):
                anchors.append((x, y))
    index = 0
    while production.active(Items.Weird_Substance, target) and get_time() < deadline:
        x, y = anchors[index]
        nursery_move_to(x, y, size)
        matched = False
        if get_entity_type() == Entities.Tree:
            kind, position = get_companion()
            px, py = position
            matched = kind == Entities.Grass and (px % 2 != 0 or py % 2 != 0)
            if matched and can_harvest():
                if not use_item(Items.Fertilizer) or not harvest():
                    quick_print("nursery_failed", "infect_or_harvest", worker)
                    return False
                matched = False
                if not production.active(Items.Weird_Substance, target):
                    return True
            elif not matched:
                if not harvest():
                    return False
        if not matched:
            for attempt in range(128):
                if get_time() >= deadline:
                    return True
                if not plant(Entities.Tree):
                    return False
                kind, position = get_companion()
                px, py = position
                if kind == Entities.Grass and (px % 2 != 0 or py % 2 != 0):
                    matched = True
                    break
                harvest()
            if not matched:
                quick_print("nursery_failed", "companion", worker)
                return False
        if get_water() < 0.5 and num_items(Items.Water) >= 2:
            use_item(Items.Water, 2)
        index = (index + 1) % len(anchors)
    return True


def nursery_move_to(x, y, size):
    dx = (x - get_pos_x()) % size
    dy = (y - get_pos_y()) % size
    direction = East
    if dx > size // 2:
        direction = West
        dx = size - dx
    for _ in range(dx):
        move(direction)
    direction = North
    if dy > size // 2:
        direction = South
        dy = size - dy
    for _ in range(dy):
        move(direction)


if __name__ == "__main__":
    weird_substance()
