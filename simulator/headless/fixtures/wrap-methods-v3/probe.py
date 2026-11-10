from __builtins__ import *

def wrap_methods():
    clear()
    size = get_world_size()
    original = get_ground_type()
    placed = place(Grounds.Block_Red)
    if not move(West):
        quick_print("wrap_done", False, "move_west")
        return
    x = get_pos_x()
    ground = get_ground_type(East)
    z = get_pos_z(East)
    hardness = get_hardness(East)
    stability = get_stability(East)
    quick_print("wrap_queries", x, ground, z, hardness, stability)
    if not move(East):
        quick_print("wrap_done", False, "move_east")
        return
    allowed = can_push(West)
    pushed = push(West)
    source = get_ground_type()
    target = get_ground_type(West)
    target_z = get_pos_z(West)
    quick_print("wrap_push", allowed, pushed, source, target, target_z)
    if not move(West):
        quick_print("wrap_done", False, "target_move")
        return
    actual = get_ground_type()
    opposite = get_ground_type(East)
    quick_print("wrap_target", get_pos_x(), actual, opposite)
    ok = placed and x == size - 1 and ground == Grounds.Block_Red and z == 1
    ok = ok and hardness == None and stability == None and not allowed and not pushed
    ok = ok and source == Grounds.Block_Red and target == original and target_z == 0
    ok = ok and actual == original and opposite == Grounds.Block_Red
    # 彩块不可推；再用实际生成的蘑菇和更低的西侧邻柱验证成功推送。
    if not move(East) or get_ground_type() != Grounds.Block_Red or not dig():
        quick_print("wrap_done", False, "remove_probe_block")
        return
    for _ in range(256):
        if get_ground_type() == Grounds.Mushroom:
            break
        if get_hardness() >= 10000000 or not dig():
            quick_print("wrap_done", False, "mushroom_search")
            return
    if get_ground_type() != Grounds.Mushroom:
        quick_print("wrap_done", False, "no_mushroom")
        return
    source_z = get_pos_z()
    if not move(West):
        quick_print("wrap_done", False, "mushroom_west")
        return
    for _ in range(256):
        if get_pos_z() < source_z:
            break
        if get_hardness() >= 10000000 or not dig():
            quick_print("wrap_done", False, "target_prepare")
            return
    lower_z = get_pos_z()
    if not move(East):
        quick_print("wrap_done", False, "mushroom_east")
        return
    kind = get_ground_type()
    allowed = can_push(West)
    pushed = push(West)
    quick_print("wrap_mushroom_push", source_z, lower_z, kind, allowed, pushed, get_ground_type(), get_ground_type(West), get_pos_z(), get_pos_z(West), num_items(Items.Mushroom))
    ok = ok and kind == Grounds.Mushroom and lower_z < source_z and allowed and pushed
    quick_print("wrap_done", ok, get_time())

if __name__ == "__main__":
    wrap_methods()
