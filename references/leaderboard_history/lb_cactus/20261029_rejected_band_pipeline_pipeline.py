# 淘汰候选归档：lb_cactus | 原实验路径 .codex/leaderboard-astra/cactus-band-pipeline/pipeline.py
def lb_cactus():
    set_world_size(32)
    clear()
    upper = spawn_drone(band, 16)
    band(0)
    if upper == None:
        band(16)
    else:
        wait_for(upper)
    quick_print("bands_ready", get_time())
    dispatch_lines(0, 32, True)
    quick_print("merged", get_time())
    goto(0, 31)
    harvest()
    return num_items(Items.Cactus) >= 33554432


def band(bottom):
    dispatch_band_lines(0, 16, bottom, False)
    quick_print("band_rows", bottom, get_time())
    dispatch_band_lines(0, 16, bottom, True)
    quick_print("band_columns", bottom, get_time())


def dispatch_band_lines(first, count, bottom, columns):
    handles = []
    while count > 1:
        left = count // 2
        handle = spawn_drone(dispatch_band_lines, first + left, count - left, bottom, columns)
        if handle == None:
            dispatch_band_lines(first + left, count - left, bottom, columns)
        else:
            handles.append(handle)
        count = left
    index = 15 - first
    if columns:
        goto(index, bottom)
        sort_one_way("y", bottom, bottom + 15)
        goto(index + 16, bottom)
        sort_one_way("y", bottom, bottom + 15)
    else:
        goto(0, bottom + index)
        plant_and_sort_x()
    for handle in handles:
        wait_for(handle)
