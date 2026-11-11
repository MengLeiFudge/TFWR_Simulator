from __builtins__ import *
import production

# 与建材入口使用同一机制：连续深入新地层，收取原生爆破的实际掉落。
DYNAMITE_RESERVE = 2000


def mine(item, target=-1):
    if not production.active(item, target):
        return
    if num_drones() != 1:
        quick_print("请等待其他无人机结束，再开始连续深钻。")
        return
    set_world_size(32)
    clear()
    change_hat(Hats.Explosive_Drill)
    production.jump_once(Unlocks.Dynamite)
    steps = 0
    while production.active(item, target):
        if steps % 16 == 0 and get_hardness() >= 10000000:
            quick_print("深钻达到硬度边界，停止：", item, get_pos_z())
            return
        if num_items(Items.Dynamite) < 1 or not dig():
            quick_print("炸药不足或挖掘失败，停止：", item)
            return
        steps += 1
        if steps % 256 == 0:
            quick_print("mining_cycle", item, get_time(), num_items(item), get_pos_z())
