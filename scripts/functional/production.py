from __builtins__ import *

# Jump 属于整次执行的额度，独立于各资源的库存目标。
JUMP_USED = False


# 在可正常结算的位置检查最终库存；默认持续生产。
def active(item, target):
    return target == -1 or num_items(item) < target


# Jump 属于整次执行的额度；切换资源或 clear 后也不能再次使用。
def jump_once(unlock):
    global JUMP_USED
    if JUMP_USED:
        return
    jump(unlock)
    JUMP_USED = True
