from __builtins__ import *
import dynamite
# 炸药排除、炸药排除专家：32×32田下到-600以下，完整揭开一层哑弹。
# 复用常规求解器；无确定安全格时换田，不把引爆后的部分得分当作成功。
MAX_GAME_SECONDS = 300


def dynamite_expert():
    deadline = get_time() + MAX_GAME_SECONDS - 5
    set_world_size(32)
    near = []
    for cell in range(1024):
        near.append(dynamite.neighbors(cell, 32))
    for attempt in range(8):
        if get_time() >= deadline:
            break
        clear()
        dynamite.move_to(16, 16, 32)
        change_hat(Hats.Explosive_Drill)
        while get_pos_z() > -600 and get_time() < deadline:
            if num_items(Items.Dynamite) < 1 or not dig():
                quick_print("炸药不足或深钻失败。")
                return
        change_hat(Hats.Mining_Hat)
        while get_ground_type() != Grounds.Dynamite and get_pos_z() > -1000:
            if get_time() + get_hardness() / (1.5 ** num_unlocked(Unlocks.Mining)) >= deadline:
                quick_print("5分钟预算内未找到可解地层。")
                return
            if get_hardness() >= 10000000 or not dig():
                return
        if get_ground_type() != Grounds.Dynamite:
            quick_print("-600至-1000内未找到炸药层，换田。")
            continue
        depth = get_pos_z()
        if depth > -600:
            break
        status, number = dynamite.open_ground(depth, deadline)
        if status == "number":
            status, rounds = dynamite.solve(32, depth, near, number, deadline, False)
        quick_print("炸药专家盘：", attempt + 1, "深度", depth, "状态", status, "游戏时间", get_time())
        if status == "ended":
            quick_print("已完整揭开-600以下炸药层的全部哑弹。")
            return
    quick_print("5分钟或8盘预算内未完整解盘；已停止并回收子机。")


if __name__ == "__main__":
    dynamite_expert()
