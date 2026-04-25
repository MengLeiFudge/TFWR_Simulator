from __builtins__ import *


# 单无人机A*寻路迷宫算法 by blac
# 未适配多无人机，并且有些地方效率不高

clear()
# set_world_size(8)
size = get_world_size()
for i in range(size // 2):
    move(North)
    move(East)
plant(Entities.Bush)
amount = size * 2**(num_unlocked(Unlocks.Mazes) - 1)
use_item(Items.Weird_Substance, amount)
run = 0

all_dir = [North, East, South, West]
dir_pos = {North: (0, 1), East: (1, 0), South: (0, -1), West: (-1, 0)}
opp_dir = {North: South, East: West, South: North, West: East}

maze = []
for i in range(size):
    maze.append([])
    for j in range(size):
        maze[i].append({North: 0, East: 0, South: 0, West: 0, "visited": False})

def pos_valid(pos):
    x, y = pos
    return 0 <= x < size and 0 <= y < size

def distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def heuristic(pos, goal):
    return distance(pos, goal)

confidence_threshold = 0
size1 = size - 1
def get_neighbors(pos):
    global confidence_threshold
    x, y = pos
    neighbors = []
    if not (maze[x][y][West ] > confidence_threshold or x == 0):
        neighbors.append((x - 1, y))
    if not (maze[x][y][East ] > confidence_threshold or x == size1):
        neighbors.append((x + 1, y))
    if not (maze[x][y][South] > confidence_threshold or y == 0):
        neighbors.append((x, y - 1))
    if not (maze[x][y][North] > confidence_threshold or y == size1):
        neighbors.append((x, y + 1))
    return neighbors

def get_relative_dir(pos, neighbor):
    x, y = pos
    x2, y2 = neighbor
    if x2 == x - 1:
        return West
    elif x2 == x + 1:
        return East
    elif y2 == y - 1:
        return South
    elif y2 == y + 1:
        return North
    return None
avg_insert_pos = 0
insert_count = 0
# 插入排序维护open_set的有序性
# 优化为二分插入排序，查找插入位置的时间复杂度从O(n)降低到O(log n)
def binary_insert_sort(l, value):
    # 计算value的f值
    f_value = value["f_value"]
    
    # 二分查找找到正确的插入位置
    left, right = 0, len(l)
    while left < right:
        mid = (left + right) // 2
        if l[mid]["f_value"] < f_value:
            left = mid + 1
        else:
            right = mid
    global insert_count
    global avg_insert_pos
    insert_count += 1
    avg_insert_pos += left / (len(l) + 1)
    
    # 在找到的位置插入元素
    l.insert(left, value)

# 替换为二分插入排序的A*算法
def astar(start, goal):
    for i in range(size):
        for j in range(size):
            maze[i][j]["visited"] = False

    open_set = [{"pos": start, "path": [], "g_value": 0, "h_value": heuristic(start, goal), "f_value": heuristic(start, goal)}]

    while open_set:
        current = open_set.pop(0)
        x, y = current["pos"]
        maze[x][y]["visited"] = True
        
        if current["pos"] == goal:
            current["path"].append(current["pos"])
            return current["path"][:]
        
        for neighbor in get_neighbors(current["pos"]):
            x2, y2 = neighbor
            if maze[x2][y2]["visited"]:
                continue

            in_open_set = False
            for node in open_set:
                if node["pos"] == neighbor:
                    in_open_set = True
                    if current["g_value"] + 1 < node["g_value"]:
                        new_node = {"pos": neighbor, "path": current["path"][:], "g_value": current["g_value"] + 1, "h_value": heuristic(neighbor, goal), "f_value": current["g_value"] + 1 + heuristic(neighbor, goal)}
                        new_node["path"].append(current["pos"])
                        open_set.remove(node)
                        binary_insert_sort(open_set, new_node)
                        break

            if not in_open_set:
                new_node = {"pos": neighbor, "path": current["path"][:], "g_value": current["g_value"] + 1, "h_value": heuristic(neighbor, goal), "f_value": current["g_value"] + 1 + heuristic(neighbor, goal)}
                new_node["path"].append(current["pos"])
                binary_insert_sort(open_set, new_node)
    return None

def get_wall(pos):
    x, y = pos
    for dir in all_dir:
        if can_move(dir):
            has_wall = 0
        else:
            has_wall = run
        maze[x][y][dir] = has_wall

        neighbors = (x + dir_pos[dir][0], y + dir_pos[dir][1])
        if pos_valid(neighbors):
            maze[neighbors[0]][neighbors[1]][opp_dir[dir]] = has_wall

while True:
    run += 1
    x = get_pos_x()
    y = get_pos_y()
    get_wall((x, y))
    while (get_pos_x(), get_pos_y()) != measure():
        path = astar((get_pos_x(), get_pos_y()), measure())[1:]
        for i in path:
            x, y = i
            dir = get_relative_dir((get_pos_x(), get_pos_y()), (x, y))
            if not can_move(dir):
                break
            move(dir)
            get_wall((x, y))
    use_item(Items.Weird_Substance, amount)
    confidence_threshold = run / 30
    if get_entity_type() == Entities.Treasure:
        harvest()
        break
quick_print("插入排序平均插入位置: ", avg_insert_pos / insert_count)