from __builtins__ import *

# 未启用调度时，各功能脚本保持持续生产；派工前的配置随无人机环境复制。
CURRENT_ITEM = None
TARGET = -1
DEADLINE = 0
JUMP_USED = False


# 冻结本次库存下限和轮转时间；完整结算周期可以晚于时间边界结束。
def begin(item, target, seconds):
    global CURRENT_ITEM
    global TARGET
    global DEADLINE
    CURRENT_ITEM = item
    TARGET = target
    DEADLINE = get_time() + seconds


# 全部子机回收后解除本次限制，避免影响后续直接调用。
def end():
    global CURRENT_ITEM
    CURRENT_ITEM = None


# 各算法只在可安全返回的位置检查；-1 只受轮转时间限制。
def active(item):
    if CURRENT_ITEM != item:
        return True
    if TARGET != -1 and num_items(item) >= TARGET:
        return False
    return get_time() < DEADLINE


# 有既定批量目标的算法仍使用原批量，上限不超过本次有限库存目标。
def goal(item, batch_target):
    if CURRENT_ITEM == item and TARGET != -1:
        return min(TARGET, batch_target)
    return batch_target


# Jump 属于整次执行的额度；切换资源或 clear 后也不能再次使用。
def jump_once(unlock):
    global JUMP_USED
    if JUMP_USED:
        return
    jump(unlock)
    JUMP_USED = True
