from __builtins__ import *
import production

# 连续向下爆破，利用原生炸药层传播；不反复回到浅层丢弃已打开的深孔。
DYNAMITE_RESERVE = 2000
ACHIEVEMENT_SECONDS = 60
ACHIEVEMENT_BLOCKS = 1000000
SAMPLE_INTERVAL = 16


# 保留库存目标与持续入口；只占用一台无人机和唯一爆破钻，按固定间隔核对库存。
def block(target=-1):
    if not production.active(Items.Block, target):
        return True
    if num_drones() != 1:
        quick_print("建材采集需要独立启动，请先等待其他无人机结束。")
        return False
    window = [(get_time(), num_items(Items.Block))]
    head = 0
    marked = False
    set_world_size(32)
    clear()
    change_hat(Hats.Explosive_Drill)
    production.jump_once(Unlocks.Dynamite)
    steps = 0
    while True:
        if target != -1 and steps % SAMPLE_INTERVAL == 0 and not production.active(Items.Block, target):
            return True
        if steps % SAMPLE_INTERVAL == 0 and get_hardness() >= 10000000:
            quick_print("建材深钻到达不可挖层，停止：z", get_pos_z())
            return False
        if not dig():
            quick_print("建材深钻失败或炸药不足，停止：z", get_pos_z())
            return False
        steps += 1
        if steps % SAMPLE_INTERVAL != 0:
            continue
        now = get_time()
        stock = num_items(Items.Block)
        window.append((now, stock))
        while now - window[head][0] > ACHIEVEMENT_SECONDS:
            head += 1
        gained = stock - window[head][1]
        if not marked and gained >= ACHIEVEMENT_BLOCKS:
            quick_print("采矿大师数量条件已达到：窗口游戏秒", now - window[head][0], "实际净增", gained, "Block。")
            marked = True
        if (steps // SAMPLE_INTERVAL) % 16 == 0:
            quick_print("block_drill", steps, "z", get_pos_z(), "游戏时间", now, "窗口净增", gained)
        # 只按下标淘汰旧窗口，避免每次从列表头删除而反复搬移全部历史。
        if head >= 1024:
            window = window[head:]
            head = 0
if __name__ == "__main__":
    block()
