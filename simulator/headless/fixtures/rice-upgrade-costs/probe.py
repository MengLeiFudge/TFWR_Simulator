from __builtins__ import *


def rice_upgrade_costs_probe():
    cost4 = get_cost(Unlocks.Rice)[Items.Block]
    before = num_items(Items.Block)
    quick_print("rice_cost_before", num_unlocked(Unlocks.Rice), cost4, before)
    fourth = unlock(Unlocks.Rice)
    after4 = num_items(Items.Block)
    cost5 = get_cost(Unlocks.Rice)[Items.Block]
    quick_print("rice_cost_after4", fourth, num_unlocked(Unlocks.Rice), cost5, after4)
    fifth = unlock(Unlocks.Rice)
    after5 = num_items(Items.Block)
    quick_print("rice_cost_after5", fifth, num_unlocked(Unlocks.Rice), after5)
    ok = cost4 == 1000 and cost5 == 2000 and fourth and fifth
    ok = ok and before == 3000 and after4 == 2000 and after5 == 0
    quick_print("rice_upgrade_done", ok, get_time())


if __name__ == "__main__":
    rice_upgrade_costs_probe()
