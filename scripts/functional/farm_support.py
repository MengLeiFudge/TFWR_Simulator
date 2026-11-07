from __builtins__ import *

# 功能脚本共用导航、科技检查、补料和普通地表种植；每次补料都在子机回收后进行。


def require(tech):
    # 不自动购买科技，避免改变用户的解锁计划。
    if num_unlocked(tech) < 1:
        quick_print("缺少前置科技，停止：", tech)
        return False
    return True


def dimensions():
    # Expand=1是1×3，get_world_size只返回高度。
    size = get_world_size()
    width = size
    if num_unlocked(Unlocks.Expand) == 1:
        width = 1
    return width, size


def capacity():
    # 未解锁Megafarm时不调用多机接口。
    if num_unlocked(Unlocks.Megafarm) < 1:
        return 1
    return max_drones()


def move_to(tx, ty):
    # 横纵轴分别按实际长度环绕，低级长条地图不会走到不存在的列。
    width, size = dimensions()
    if tx < 0 or tx >= width or ty < 0 or ty >= size:
        return False
    dx = (tx - get_pos_x()) % width
    direction = East
    if dx > width // 2:
        direction = West
        dx = width - dx
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


def water():
    # 水来自被动补给；没有浇水科技时按自然生长运行。
    if num_unlocked(Unlocks.Watering) > 0:
        if get_water() < 0.5 and num_items(Items.Water) > 0:
            use_item(Items.Water)


def mature(kind):
    # 等待有上限，异常地形或实体消失交给调用者报告。
    for _ in range(1024):
        if get_entity_type() != kind:
            return False
        if can_harvest():
            return True
        water()
        do_a_flip()
    quick_print("作物在等待上限内未成熟：", kind)
    return False


def seeds(kind, count):
    # 先筹足整批种子，再开始清场与派工；补料可能使用其他农田。
    cost = get_cost(kind)
    for item in cost:
        if not stock(item, cost[item] * count):
            return False
    return True


def stock(item, goal):
    # 各机制的有限收集入口只在主机调用，依赖按需导入且均在同目录。
    if num_items(item) >= goal:
        return True
    quick_print("补充资源：", item, "目标库存", goal)
    if item == Items.Hay:
        return farm(Entities.Grass, item, goal)
    if item == Items.Wood:
        return farm(Entities.Bush, item, goal)
    if item == Items.Carrot:
        return farm(Entities.Carrot, item, goal)
    if item == Items.Pumpkin:
        import pumpkin
        return pumpkin.collect(goal)
    if item == Items.Cactus:
        import cactus
        return cactus.collect(goal)
    if item == Items.Rice:
        import rice
        return rice.collect(goal)
    if item == Items.Weird_Substance:
        import weird_substance
        return weird_substance.collect(goal)
    if item == Items.Block or item == Items.Coal or item == Items.Iron or item == Items.Quartz:
        return mine(item, goal)
    if item == Items.Water or item == Items.Fertilizer:
        tech = Unlocks.Watering
        if item == Items.Fertilizer:
            tech = Unlocks.Fertilizer
        if not require(tech):
            return False
        while num_items(item) < goal:
            do_a_flip()
        return True
    quick_print("没有可用的补给方式，停止：", item)
    return False


def run(item, collector):
    # 每批从当前库存增加目标，达到一批后继续；不使用排行榜固定目标。
    if num_unlocked(Unlocks.Megafarm) > 0 and num_drones() > 1:
        quick_print("请等待其他无人机结束，再启动功能脚本。")
        return
    width, size = dimensions()
    while True:
        before = num_items(item)
        if not collector(before + max(1, width * size)):
            quick_print("资源生产停止：", item, "当前库存", num_items(item))
            return
        if num_items(item) <= before:
            quick_print("本批没有获得目标资源，停止：", item)
            return
        quick_print("资源生产：", item, "增加", num_items(item) - before, "库存", num_items(item))


def farm(kind, item, goal):
    # 每列独占，批次之间回收全部子机再补充种子；无无人机科技时走同一串行路径。
    if kind != Entities.Grass and not require(Unlocks.Plant):
        return False
    if num_unlocked(kind) < 1:
        quick_print("作物尚未解锁：", kind)
        return False
    width, size = dimensions()
    while num_items(item) < goal:
        if not seeds(kind, width * size):
            return False
        clear()
        workers = min(width, capacity())
        handles = []
        ok = True
        for first in range(1, workers):
            handle = spawn_drone(farm_columns, first, workers, width, size, kind)
            if handle == None:
                if not farm_columns(first, workers, width, size, kind):
                    ok = False
            else:
                handles.append(handle)
        if not farm_columns(0, workers, width, size, kind):
            ok = False
        for handle in handles:
            if not wait_for(handle):
                ok = False
        if not ok:
            quick_print("地表种植或收获失败：", kind)
            return False
    return True


def farm_columns(first, stride, width, size, kind):
    # Bush可在早期生产Wood；解锁Tree后用奇偶布局避免相邻树的成熟惩罚。
    for x in range(first, width, stride):
        for y in range(size):
            if not move_to(x, y):
                return False
            crop = kind
            if kind == Entities.Bush and num_unlocked(Entities.Tree) > 0 and (x + y) % 2 == 0:
                crop = Entities.Tree
            if crop == Entities.Grass:
                if get_ground_type() != Grounds.Grassland:
                    till()
            else:
                if get_entity_type() != None and not harvest():
                    return False
                if crop == Entities.Carrot:
                    if get_ground_type() != Grounds.Soil:
                        till()
                if not plant(crop):
                    return False
            water()
        for y in range(size):
            if not move_to(x, y):
                return False
            crop = get_entity_type()
            if crop != None and not mature(crop):
                return False
            if crop != None and not harvest():
                return False
    return True


def mine(item, goal):
    # 普通地形按层降低全场高度，只把dig实际增加的库存计为收益。
    if not require(Unlocks.Mining):
        return False
    tech = None
    if item == Items.Coal:
        tech = Unlocks.Coal
    elif item == Items.Iron:
        tech = Unlocks.Iron
    elif item == Items.Quartz:
        tech = Unlocks.Quartz
    if tech != None and not require(tech):
        return False
    width, size = dimensions()
    empty = 0
    while num_items(item) < goal:
        clear()
        before = num_items(item)
        layers = 256
        if item == Items.Coal and num_unlocked(Unlocks.Rice) > 0:
            layers = 16
        workers = min(width, capacity())
        for layer in range(layers):
            handles = []
            results = []
            for first in range(1, workers):
                handle = spawn_drone(mine_columns, first, workers, layer, item, goal)
                if handle == None:
                    results.append(mine_columns(first, workers, layer, item, goal))
                else:
                    handles.append(handle)
            results.append(mine_columns(0, workers, layer, item, goal))
            for handle in handles:
                results.append(wait_for(handle))
            active = 0
            for result in results:
                if result < 0:
                    return False
                active += result
            if num_items(item) >= goal:
                return True
            if active == 0:
                break
        if num_items(item) == before:
            empty += 1
            if empty >= 8:
                quick_print("连续八片没有获得矿物，停止：", item)
                return False
        else:
            empty = 0
    return True


def mine_columns(first, stride, layer, item, goal):
    # 每列唯一写者；有地下感知才按高度和硬度判断，否则按公开地面避开基岩。
    width, size = dimensions()
    senses = num_unlocked(Unlocks.Underground_Senses) > 0
    active = 0
    for x in range(first, width, stride):
        for y in range(size):
            if num_items(item) >= goal:
                return active
            if not move_to(x, y):
                return -1
            if get_ground_type() == Grounds.Bedrock:
                continue
            if senses:
                if get_pos_z() < -layer or get_hardness() >= 10000000:
                    continue
            if not dig():
                return -1
            active += 1
    return active
