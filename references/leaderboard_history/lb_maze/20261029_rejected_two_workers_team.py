# 淘汰候选归档：lb_maze | 原实验路径 .codex/leaderboard-astra/maze-two-workers/team.py
def solve_one(n, bx, by, grid, mapped, blank):
    p, links, walls, tree = mapped
    routes = build_all_routes(tree, blank)
    def partner():
        return serve(n, bx, by, grid, p, links, walls, routes, 1)
    handle = spawn_drone(partner)
    if handle == None:
        return None
    left, local_ok = serve(n, bx, by, grid, p, links, walls, routes, 0)
    right, other_ok = wait_for(handle)
    if not local_ok or not other_ok:
        return None
    return left + right


def serve(n, bx, by, grid, p, links, walls, routes, side):
    # 按宝箱x坐标唯一分派；双方不会对同一箱子执行兑现动作。
    # 初始图由spawn复制，后续各自发现新边；旧边不会关闭。
    cost = n * MULT
    home = (n // 2) * n + n // 4 + side * (n // 2)
    boxes = 0
    while num_items(Items.Gold) < TARGET_GOLD:
        target = measure()
        if target == None:
            # 另一责任机收掉第301箱后，本宫消失；父机等待双方退出再重建。
            return (boxes, True)
        goal = (target[1] - by) * n + target[0] - bx
        owner = 0
        if target[0] - bx >= n // 2:
            owner = 1
        if owner == side:
            if len(walls[p]) > 0:
                scan_departure(p, links, walls, grid, routes)
            dist, hop = routes[goal]
            for _ in range(dist[p]):
                p, direction = hop[p]
                if not move(direction):
                    return (boxes, False)
            if num_items(Items.Gold) >= TARGET_GOLD:
                return (boxes, True)
            if num_items(Items.Weird_Substance) < cost:
                return (boxes, False)
            if use_item(Items.Weird_Substance, cost):
                boxes += 1
            else:
                # 唯一责任者、足额材料、足额尺寸；正常失败表示已满300次迁移。
                # 前一次use_item已支付200t，且期间有measure与分支，不在结算窗重入。
                if get_entity_type() != Entities.Treasure or not harvest():
                    return (boxes, False)
                boxes += 1
                return (boxes, True)
        elif p != home:
            # 非责任者逐步回本半区中心，每步后重新读取目标，不追同一箱子聚集。
            p, direction = routes[home][1][p]
            if not move(direction):
                return (boxes, False)
        else:
            for _ in range(32):
                pass
    return (boxes, True)
