from __builtins__ import *
# 放置、建造者、大建造者、毕加索：16机反复放置彩色块再挖回，累计10000次。
MAX_GAME_SECONDS = 300
PLACEMENTS = 10000


def block_builder():
    deadline = get_time() + MAX_GAME_SECONDS - 2
    set_world_size(4)
    clear()
    if max_drones() - num_drones() < 15:
        quick_print("需要16台可用无人机。")
        return
    handles = []
    for cell in range(15):
        handles.append(spawn_drone(build_worker, deadline))
        move(East)
        if cell % 4 == 3:
            move(North)
    done = build_worker(deadline)
    for handle in handles:
        done += wait_for(handle)
    quick_print("本次彩色块放置次数：", done, "目标：", PLACEMENTS)


def build_worker(deadline):
    change_hat(Hats.Mining_Hat)
    done = 0
    while done < PLACEMENTS // 16 and get_time() < deadline:
        if not place(Grounds.Block_Red):
            break
        done += 1
        if not dig():
            break
    return done


if __name__ == "__main__":
    block_builder()
