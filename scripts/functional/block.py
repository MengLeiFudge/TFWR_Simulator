from __builtins__ import *
import mining
import production

# 多机常驻布置炸药网；向日葵种子消耗标记就绪，主机用唯一爆破钻触发连锁收集。
ROUNDS_PER_FIELD = 16
FIELD_GAME_SECONDS = 15
ACHIEVEMENT_SECONDS = 60
ACHIEVEMENT_BLOCKS = 1000000


# 保留库存目标入口；每田全部子机返回后才清场，窗口只计实际Block库存增长。
def block(target=-1):
    if not production.active(Items.Block, target):
        return True
    if num_drones() != 1:
        quick_print("建材采集需要独立启动，请先等待其他无人机结束。")
        return False
    size = get_world_size()
    points = []
    for row in range((size + 3) // 4):
        for column in range((size + 3) // 4):
            points.append((min(size - 1, 2 + column * 4), min(size - 1, 2 + row * 4)))
    workers = min(max_drones(), (len(points) + 1) // 2)
    jobs = []
    for _ in range(workers):
        jobs.append([])
    for index in range(len(points)):
        jobs[(index // 2) % len(jobs)].append(points[index])
    fuse = ((jobs[0][-1][0] + 1) % size, jobs[0][-1][1])
    window = [(get_time(), num_items(Items.Block))]
    # 每机一块土台；当前库存不足时先手挖启动，成本仍包含在60秒窗口内。
    if num_items(Items.Block) < workers:
        clear()
        change_hat(Hats.Mining_Hat)
        for _ in range(workers * 4):
            if num_items(Items.Block) >= workers or not production.active(Items.Block, target):
                break
            if get_hardness() >= 10000000 or not dig():
                return False
        if not production.active(Items.Block, target):
            return True
        if num_items(Items.Block) < workers:
            quick_print("建材启动材料不足，手挖达到次数上限。")
            return False
    seed_cost = get_cost(Entities.Sunflower)[Items.Carrot]
    marked = False
    empty = 0
    cycle = 0
    while production.active(Items.Block, target):
        materials = num_items(Items.Dynamite)
        carrots = num_items(Items.Carrot)
        rounds = min(ROUNDS_PER_FIELD, materials // (len(points) + 1), carrots // (workers * seed_cost))
        if rounds < 1:
            quick_print("建材连锁爆破材料不足：每轮需要Dynamite", len(points) + 1, "Carrot", workers * seed_cost, "当前", materials, carrots)
            return False
        clear()
        change_hat(Hats.Explosive_Drill)
        deadline = get_time() + FIELD_GAME_SECONDS
        before = num_items(Items.Block)
        handles = []
        ok = True
        for owner in range(1, workers):
            handle = spawn_drone(block_worker, jobs[owner], size, workers, rounds, target, deadline)
            if handle == None:
                ok = False
                break
            handles.append(handle)
        if ok:
            for phase in range(rounds):
                if not production.active(Items.Block, target):
                    break
                ready = block_plant(jobs[0], size, workers, target, deadline)
                if ready != True:
                    if ready == False:
                        ok = False
                    break
                # 原生炸药层会额外产Dynamite；只用地下不会产出的Carrot种子消费作屏障。
                threshold = carrots - (phase + 1) * workers * seed_cost
                while num_items(Items.Carrot) > threshold and num_drones() == workers:
                    if get_time() >= deadline or not hover(1):
                        ok = False
                        break
                if not ok or num_drones() != workers:
                    break
                if not mining.move_to(fuse[0], fuse[1], size):
                    ok = False
                    break
                # 在自己的向日葵标记格点火，避免炸药实体先执行不收掉落的普通爆炸。
                ground = get_ground_type()
                if get_entity_type() == Entities.Dynamite or ground == Grounds.Soot or ground == Grounds.Dynamite:
                    quick_print("点火格进入原生炸药层，停止本次采集。")
                    ok = False
                    break
                window.append((get_time(), num_items(Items.Block)))
                if get_time() >= deadline or get_hardness() >= 10000000 or not dig():
                    ok = False
                    break
                now = get_time()
                stock = num_items(Items.Block)
                window.append((now, stock))
                while len(window) > 1 and now - window[0][0] > ACHIEVEMENT_SECONDS:
                    window.pop(0)
                gained = stock - window[0][1]
                quick_print("block_blast", cycle, phase + 1, "本田净增", stock - before, "窗口秒", now - window[0][0], "窗口净增", gained)
                if not marked and gained >= ACHIEVEMENT_BLOCKS:
                    quick_print("采矿大师数量条件已达到：60游戏秒以内实际净增", gained, "Block。")
                    marked = True
        for handle in handles:
            result = wait_for(handle)
            if result == False:
                ok = False
        gained = num_items(Items.Block) - before
        quick_print("block_field", cycle, "净增", gained, "游戏时间", get_time())
        if not ok:
            quick_print("建材连锁爆破未完成，已回收子机并停止，请检查前面的动作或等待日志。")
            return False
        if gained <= 0:
            empty += 1
            if empty >= 8:
                quick_print("连续八片没有建材净增长，停止。")
                return False
        else:
            empty = 0
        cycle += 1
    return True


# 标记消失且Block高于布药前才算点火完成，避免原生炸药自爆让工人提前进入下一轮。
def block_worker(job, size, workers, rounds, target, deadline):
    while num_drones() < workers:
        if get_time() >= deadline or not hover(1):
            return False
    for _ in range(rounds):
        before = num_items(Items.Block)
        if not production.active(Items.Block, target):
            return True
        ready = block_plant(job, size, workers, target, deadline)
        if ready != True:
            return ready
        while get_entity_type() == Entities.Sunflower or num_items(Items.Block) <= before:
            if not production.active(Items.Block, target):
                return True
            if num_drones() != workers:
                return "renew"
            if get_time() >= deadline or not hover(1):
                quick_print("建材工人等待连锁爆破超时：位置", get_pos_x(), get_pos_y())
                return False
    return True


# 每个网点由唯一工人写入；原生炸药层交给主机回收后换田，动作失败单独报告。
def block_plant(job, size, workers, target, deadline):
    for x, y in job:
        if not production.active(Items.Block, target):
            return "renew"
        if num_drones() != workers:
            return "renew"
        if get_time() >= deadline or not mining.move_to(x, y, size):
            quick_print("建材布药移动失败或达到时间上限：目标", x, y)
            return False
        ground = get_ground_type()
        if ground == Grounds.Soot or ground == Grounds.Dynamite:
            quick_print("建材网点到达原生炸药层：位置", x, y, get_pos_z())
            return "renew"
        if get_entity_type() == Entities.Dynamite or not plant(Entities.Dynamite):
            quick_print("建材布药失败或上轮炸药尚未引爆：位置", x, y, get_pos_z())
            return False
    marker = ((job[-1][0] + 1) % size, job[-1][1])
    if get_time() >= deadline or not mining.move_to(marker[0], marker[1], size):
        return False
    if get_entity_type() == Entities.Sunflower or num_items(Items.Block) < 1 or not place(Grounds.Dirt):
        quick_print("建材就绪土台放置失败或上轮标记未清除：位置", marker)
        return False
    till()
    if get_ground_type() != Grounds.Soil or not plant(Entities.Sunflower):
        quick_print("建材就绪向日葵种植失败：位置", marker)
        return False
    return True


if __name__ == "__main__":
    block()
