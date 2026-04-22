from __builtins__ import *


# Maze single 版本结论
# main1: 2x2 世界，4 格全种 Bush 再连续使用 Weird_Substance 开 2x2 mini-maze。
#        entities.TreasureView.reposition_treasure 里每次 use_item 命中 Treasure
#        就加 S*S=4 gold，treasure_factor 最多 301 次；后续再来一次用 harvest
#        结算当前 Treasure 再拿 S*S=4 gold，整轮约 301*4 + 4 = 1208 gold。
#        目标 616448 / 1208 ≈ 510 轮。本版先跑通；后续可试 4x4 的 16 gold/次 对比。


def main1():
    set_world_size(2)
    goal = 616448
    # Mazes=6 时 divisor=32；amount/divisor = desired_size。amount=64 对应 2x2 子迷宫。
    substance = 2 * (2 ** (num_unlocked(Unlocks.Mazes) - 1))
    while num_items(Items.Gold) < goal:
        # 若当前格已是上一轮残留 Hedge/Treasure，先清；再种 Bush 重建迷宫。
        entity = get_entity_type()
        if entity != None and entity != Entities.Bush:
            harvest()
        plant(Entities.Bush)
        use_item(Items.Weird_Substance, substance)
        # 连续撒物质直到 treasure_factor 饱和 (301 次后 reposition_treasure 返回 False)；
        # 实测 301 次后继续 use_item 不再给 gold，改为 harvest 拿收尾那一份。
        for _ in range(301):
            if num_items(Items.Gold) >= goal:
                break
            use_item(Items.Weird_Substance, substance)
        if get_entity_type() == Entities.Treasure:
            harvest()
    quick_print("main1 done gold=", num_items(Items.Gold), " time=", get_time())


if __name__ == "__main__":
    main1()
