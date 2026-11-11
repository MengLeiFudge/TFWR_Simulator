from __builtins__ import *
# 杂技高手、杂技大师：并行完成累计1000次翻转，全部子机结束后返回。
MAX_GAME_SECONDS = 300
FLIPS = 1000


def acrobatics():
    deadline = get_time() + MAX_GAME_SECONDS - 2
    workers = max_drones()
    handles = []
    for index in range(workers - 1):
        count = FLIPS // workers
        if index < FLIPS % workers:
            count += 1
        handle = spawn_drone(flip_worker, count, deadline)
        if handle == None:
            break
        handles.append(handle)
    done = flip_worker(FLIPS // workers, deadline)
    for handle in handles:
        done += wait_for(handle)
    quick_print("本次翻转次数：", done, "目标：", FLIPS)


def flip_worker(count, deadline):
    done = 0
    while done < count and get_time() < deadline:
        do_a_flip()
        done += 1
    return done


if __name__ == "__main__":
    acrobatics()
