from __builtins__ import *
import production


# 其他资源已备足；可见矿优先追脉，否则用Coal取得当前矿柱方向。
def iron(target=-1):
    if not production.active(Items.Iron, target):
        return
    production.jump_once(Unlocks.Iron)
    first = True
    empty_fields = 0
    cycle = 0
    while production.active(Items.Iron, target):
        if not first:
            clear()
        first = False
        change_hat(Hats.Explosive_Drill)
        before = num_items(Items.Iron)
        field_start = before
        deadline = get_time() + 600
        empty_digs = 0
        for action in range(512):
            if not production.active(Items.Iron, target):
                quick_print("iron_done", True, get_time(), num_items(Items.Iron))
                return
            if get_time() > deadline:
                break
            direction = None
            if get_ground_type() != Grounds.Iron:
                # 已露矿柱和邻柱直接追脉；仅未公开下一矿柱时支付Coal。
                for nearby in [North, East, South, West]:
                    if get_ground_type(nearby) == Grounds.Iron:
                        direction = nearby
                        break
                if direction == None:
                    if num_items(Items.Coal) < 1:
                        quick_print("iron_failed", "coal")
                        return
                    direction = prospect_iron()
            if direction != None:
                if not move(direction):
                    quick_print("iron_failed", "move")
                    return
                continue
            # None也可能无矿；只按实际钻孔收益和有界深度继续。
            if get_pos_z() < -128 or get_hardness() >= 10000000:
                break
            if num_items(Items.Dynamite) < 1 or not dig():
                quick_print("iron_failed", "drill")
                return
            now = num_items(Items.Iron)
            if now > before:
                empty_digs = 0
                before = now
            else:
                empty_digs += 1
                if empty_digs >= 16:
                    break
        quick_print("iron_prospect_cycle", cycle, get_time(), num_items(Items.Iron), num_items(Items.Coal))
        if num_items(Items.Iron) <= field_start:
            empty_fields += 1
            if empty_fields >= 8:
                quick_print("iron_failed", "eight_empty_fields")
                return
        else:
            empty_fields = 0
        cycle += 1


if __name__ == "__main__":
    iron()
