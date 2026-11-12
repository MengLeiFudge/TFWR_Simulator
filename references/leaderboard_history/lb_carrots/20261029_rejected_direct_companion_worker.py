# 淘汰候选归档：lb_carrots | 原实验路径 .codex/leaderboard-astra/carrots-direct-companion/worker.py
def work_drone_task():
    def on_eachcell():
        here = (get_pos_x(), get_pos_y())
        if get_water() < W and num_items(Items.Water) > 32:
            use_item(Items.Water)
        harvest()
        plant(Entities.Carrot)
        companion = get_companion()
        # 其他机可能在本格满足自己的请求；缺失请求直接留待下次巡田。
        if companion == None:
            return
        kind, pos = companion
        direct_goto(pos)
        if get_entity_type() != kind:
            harvest()
            plant(kind)
        direct_goto(here)

    def first_round():
        till()
        on_eachcell()

    def while_round():
        on_eachcell()
        return num_items(Items.Carrot) >= 2000000000

    traverse_rectangle(first_round, 4, 8)
    while traverse_rectangle_if(while_round, 4, 8):
        continue


def direct_goto(pos):
    x, y = pos
    dx = (x - get_pos_x()) % 32
    if dx <= 16:
        for _ in range(dx):
            move(East)
    else:
        for _ in range(32 - dx):
            move(West)
    dy = (y - get_pos_y()) % 32
    if dy <= 16:
        for _ in range(dy):
            move(North)
    else:
        for _ in range(32 - dy):
            move(South)
