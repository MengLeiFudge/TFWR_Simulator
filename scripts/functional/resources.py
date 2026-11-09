from __builtins__ import *

# 在这里填写最终库存下限：0 不设目标，正整数表示至少保留该数量，-1 持续生产。
TARGETS = {
    Items.Hay: 0,                 # 干草
    Items.Wood: 0,                # 木材
    Items.Carrot: 0,              # 胡萝卜
    Items.Pumpkin: 0,             # 南瓜
    Items.Cactus: 0,              # 仙人掌
    Items.Bone: 0,                # 骨头
    Items.Weird_Substance: 0,     # 怪异物质
    Items.Gold: 0,                # 金币
    Items.Rice: 0,                # 水稻
    Items.Bamboo: 0,              # 竹子
    Items.Coal: 0,                # 煤
    Items.Mushroom: 0,            # 蘑菇
    Items.Dynamite: 0,            # 炸药
    Items.Block: 0,               # 建材
    Items.Iron: 0,                # 铁
    Items.Quartz: 0,              # 石英
    Items.Power: 0,               # 能量
    Items.Water: 0,               # 水，等待游戏自动补给
    Items.Fertilizer: 0,          # 肥料，等待游戏自动补给
}

import production


# 依次补足目标；生产中消耗掉的其他目标资源会在下一次巡检补回。
def resources():
    for item in TARGETS:
        target = TARGETS[item]
        if target < -1 or target != target // 1:
            quick_print("资源目标无效：", item, target, "；请在 TARGETS 中填写 -1 或非负整数。")
            return
    pending = False
    for item in TARGETS:
        if TARGETS[item] == -1 or num_items(item) < TARGETS[item]:
            pending = True
    if not pending:
        quick_print("所有资源已达标。")
        return
    if num_drones() != 1:
        quick_print("请等待其他无人机结束，再启动 resources。")
        return
    set_world_size(32)

    # 资源模块含按农场尺寸初始化的布局；先确定尺寸，再加载同目录模块。
    import hay
    import wood
    import carrot
    import pumpkin
    import cactus
    import bone_dinosaur
    import weird_substance
    import gold_maze
    import rice
    import bamboo
    import coal
    import mushroom
    import dynamite
    import block
    import iron
    import quartz
    import power_sunflower

    producers = {
        Items.Hay: hay.hay,
        Items.Wood: wood.wood,
        Items.Carrot: carrot.carrot,
        Items.Pumpkin: pumpkin.pumpkin,
        Items.Cactus: cactus.cactus,
        Items.Bone: bone_dinosaur.bone_dinosaur,
        Items.Weird_Substance: weird_substance.weird_substance,
        Items.Gold: gold_maze.gold_maze,
        Items.Rice: rice.rice,
        Items.Bamboo: bamboo.bamboo,
        Items.Coal: coal.coal,
        Items.Mushroom: mushroom.mushroom,
        Items.Dynamite: dynamite.dynamite,
        Items.Block: block.block,
        Items.Iron: iron.iron,
        Items.Quartz: quartz.quartz,
        Items.Power: power_sunflower.power_sunflower,
    }
    while True:
        pending = False
        for item in TARGETS:
            target = TARGETS[item]
            if target != -1 and num_items(item) < target:
                pending = True
                if not supply(item, target, producers):
                    return
        if not pending:
            break
    for item in TARGETS:
        if TARGETS[item] == -1:
            if not supply(item, -1, producers):
                return
    quick_print("所有资源已达标。")


# 直接传递库存目标；仅在已知材料不足且本次有净产出时补料重试。
def supply(item, target, producers):
    while production.active(item, target):
        needed = materials(item)
        for material in needed:
            if not supply(material, needed[material], producers):
                return False
        # 补料算法可能顺带收获本资源；先重新检查，避免达标后仍清田或误报停产。
        if not production.active(item, target):
            return True
        before = num_items(item)
        quick_print("开始补充：", item, "当前", before, "目标", target)
        if item == Items.Water or item == Items.Fertilizer:
            while production.active(item, target):
                do_a_flip()
        else:
            # 切换机制前，上一次生产的子机已全部回收。
            clear()
            producers[item](target)
            while num_drones() > 1:
                do_a_flip()
        after = num_items(item)
        quick_print("生产返回：", item, "当前", after, "净增", after - before)
        if not production.active(item, target):
            return True
        if after <= before:
            quick_print("资源未增长，停止调度：", item, "；请检查上方功能脚本日志、材料和农田条件。")
            return False
        shortage = False
        for material in needed:
            if num_items(material) < needed[material]:
                shortage = True
        if not shortage:
            quick_print("目标未完成，功能脚本提前返回，停止调度：", item, "；请检查上方日志。")
            return False
    return True


# 按现有算法的一批田块或完整周期准备材料，避免目标未配置的原料耗尽后空转。
def materials(item):
    plots = get_world_size() ** 2
    crops = {
        # 伴生重抽与死南瓜补种需要额外种子；入口因缺料返回后重新补给。
        Items.Carrot: (Entities.Carrot, plots * 8),
        Items.Pumpkin: (Entities.Pumpkin, plots * 4),
        Items.Cactus: (Entities.Cactus, plots),
        Items.Bone: (Entities.Apple, plots),
        Items.Bamboo: (Entities.Bamboo, plots * 4),
    }
    needed = {}
    if item in crops:
        crop, count = crops[item]
        cost = get_cost(crop)
        for material in cost:
            needed[material] = cost[material] * count
    if item == Items.Power:
        # 14 波向日葵和每波 9 档各 32 组的南瓜扣料信号都消耗胡萝卜。
        for crop, count in [(Entities.Sunflower, 14 * 32 * 31), (Entities.Pumpkin, 14 * 9 * 32)]:
            cost = get_cost(crop)
            for material in cost:
                if material not in needed:
                    needed[material] = 0
                needed[material] += cost[material] * count
    if item == Items.Gold:
        # 20 座 5x5、6 座 6x6、6 座 7x7，各准备一代 301 箱和初始化的 64 份。
        needed[Items.Weird_Substance] = 64 + (20 * 5 + 6 * 6 + 6 * 7) * 2 ** (num_unlocked(Unlocks.Mazes) - 1) * 301
    if item == Items.Block:
        import block
        # 连续深钻每次消耗一份炸药；材料储备由建材入口统一声明。
        needed[Items.Dynamite] = block.DYNAMITE_RESERVE
    depths = {Items.Iron: 64, Items.Quartz: 80}
    if item in depths:
        # 爆破钻头每次扣一份炸药；为覆盖层及矿层留出一批完整沟挖的库存。
        needed[Items.Dynamite] = plots * (depths[item] + 16)
    if item == Items.Iron:
        # 铁入口用Coal支付方向查询；缺料返回后由调度补齐再继续。
        needed[Items.Coal] = plots * 4
    return needed


if __name__ == "__main__":
    resources()
