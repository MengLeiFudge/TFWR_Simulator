from __builtins__ import *
# 成就入口：让5台仍在场的无人机同时佩戴不同帽子。
# 使用普通科技帽子；短暂保持同时在场，随后回收全部子机。
MAX_GAME_SECONDS = 300
HATS = [Hats.Brown_Hat, Hats.Gray_Hat, Hats.Green_Hat, Hats.Purple_Hat]


def fashion_worker(hat, deadline):
    change_hat(hat)
    while get_time() < deadline:
        do_a_flip()


def fashion_show():
    deadline = get_time() + min(2, MAX_GAME_SECONDS - 1)
    handles = []
    for hat in HATS:
        handle = spawn_drone(fashion_worker, hat, deadline)
        if handle == None:
            break
        handles.append(handle)
    change_hat(Hats.Mining_Hat)
    for handle in handles:
        wait_for(handle)
    if len(handles) == 4:
        quick_print("已让5台无人机同时佩戴不同帽子。")
    else:
        quick_print("时装秀需要至少5台可用无人机。")

if __name__ == "__main__":
    fashion_show()
