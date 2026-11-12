from __builtins__ import *
# 淘汰候选归档：lb_bamboo | 原实验路径 .codex/nonreset-100-20261108/bamboo-batch-v2/lb_bamboo.py
# 本地研究入口；并行行带各自选种和切收，尚未实机。
import lb_bamboo_single


def lb_bamboo():
    clear()
    size = get_world_size()
    workers = min(max_drones(), size)
    handles = []
    for owner in range(1, workers):
        y0 = owner * size // workers
        rows = (owner + 1) * size // workers - y0
        handle = spawn_drone(lb_bamboo_single.bamboo_batch, y0, rows, 500000000, 0.25, 3)
        if handle == None:
            quick_print("bamboo_failed", "spawn", owner)
            return
        handles.append(handle)
    ok = lb_bamboo_single.bamboo_batch(0, size // workers, 500000000, 0.25, 3)
    for handle in handles:
        if not wait_for(handle):
            ok = False
    quick_print("bamboo_all_done", ok, get_time(), num_items(Items.Bamboo))


if __name__ == "__main__":
    lb_bamboo()
