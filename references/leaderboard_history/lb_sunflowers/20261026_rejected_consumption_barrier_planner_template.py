from __builtins__ import *
# 淘汰候选归档：lb_sunflowers | 原实验路径 .codex/leaderboard-astra/sunflowers-consumption-barrier/planner/template.py
# 私有纯规划组件；固定输入不包含真实采集和同步费用。
def lb_prefix_planner():
    quick_print("prefix_begin", get_time(), get_tick_count())
    result = launch(0, 8, get_time() + 30)
    quick_print("prefix_done", result, get_time(), get_tick_count())


def launch(pod, count, deadline):
    if count == 1:
        return plan(pod, deadline)
    half = count // 2
    def child():
        return launch(pod + half, half, deadline)
    handle = spawn_drone(child)
    if handle == None:
        quick_print("prefix_failed", pod, "spawn")
        return False
    local = launch(pod, half, deadline)
    other = wait_for(handle)
    return local and other


def fill(positions, cells, order, limit, prefix, mapping):
    index = 0
    stops = []
    for pair in order:
        worker = pair[1]
        if index == len(cells):
            stops.append(index)
            continue
        entry = table[mapping[positions[worker]]][mapping[cells[index]]] + 1
        allowance = prefix[index] + limit - entry
        low = index
        high = len(cells)
        while low < high:
            middle = (low + high) // 2
            if prefix[middle] <= allowance:
                low = middle + 1
            else:
                high = middle
        index = low
        stops.append(index)
    return index == len(cells), stops


def plan(pod, deadline):
    start = get_time()
    ticks = get_tick_count()
    positions = [16, 48, 80, 112]
    mapping = codes[pod]
    for rank in range(9):
        if get_time() > deadline:
            quick_print("prefix_failed", pod, "deadline")
            return False
        began = get_tick_count()
        cells = buckets[pod][rank]
        routes = [[], [], [], []]
        loads = [0, 0, 0, 0]
        if len(cells) > 0:
            prefix = [0]
            for i in range(1, len(cells)):
                prefix.append(prefix[-1] + table[mapping[cells[i - 1]]][mapping[cells[i]]] + 1)
            order = []
            for worker in range(4):
                order.append(((positions[worker] - cells[0]) % 128, worker))
            for i in range(1, 4):
                j = i
                while j > 0 and order[j] < order[j - 1]:
                    order[j], order[j - 1] = order[j - 1], order[j]
                    j -= 1
            low = 1
            high = prefix[-1] + 32
            while low < high:
                middle = (low + high) // 2
                covered, stops = fill(positions, cells, order, middle, prefix, mapping)
                if covered:
                    high = middle
                else:
                    low = middle + 1
            covered, stops = fill(positions, cells, order, low, prefix, mapping)
            if not covered:
                quick_print("prefix_failed", pod, rank, "uncovered")
                return False
            index = 0
            for j in range(4):
                worker = order[j][1]
                stop = stops[j]
                if stop > index:
                    loads[worker] = table[mapping[positions[worker]]][mapping[cells[index]]] + 1 + prefix[stop - 1] - prefix[index]
                    routes[worker] = cells[index:stop]
                    positions[worker] = cells[stop - 1]
                index = stop
        quick_print("prefix_rank", pod, rank, get_tick_count() - began, routes, loads)
    quick_print("prefix_pod", pod, get_tick_count() - ticks, get_time() - start)
    return True
