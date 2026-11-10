from __builtins__ import *
# 成就入口：让5台仍在场的无人机同时佩戴不同帽子。
# 最长运行300游戏秒；达成后可手动停止，不进入常规生产循环。
MAX_GAME_SECONDS = 300
HATS = [Hats.Cactus_Hat, Hats.Carrot_Hat, Hats.Tree_Hat, Hats.Wizard_Hat]


def fashion_worker(hat, deadline):
    change_hat(hat)
    while get_time() < deadline:
        do_a_flip()


def fashion_show():
    deadline = get_time() + MAX_GAME_SECONDS
    handles = []
    for hat in HATS:
        handle = spawn_drone(fashion_worker, hat, deadline)
        if handle == None:
            quick_print("FASHION_SHOW 需要至少5台可用无人机。")
            return
        handles.append(handle)
    change_hat(Hats.Mining_Hat)
    for handle in handles:
        wait_for(handle)


if __name__ == "__main__":
    fashion_show()
