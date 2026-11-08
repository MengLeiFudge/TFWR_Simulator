from __builtins__ import *
import production
# ==========================================================
#  DigCoal v25  (final)
#  - round 1 uses jump for a fast start
#  - every following round after clear() runs WITHOUT jump,
#    so MAXSCAN has to be deep enough to reach coal from surface
#  - stop digging at clay, mine coal only
#  - first coal of a round aborts every other blind digger
# ==========================================================

SIZE    = get_world_size()   # 32
COLS    = 8
ROWS    = 4
MAXSCAN = 40                 # deep enough without jump
DEPTH   = 20

def goto(tx, ty):
    while get_pos_x() < tx:
        move(East)
    while get_pos_x() > tx:
        move(West)
    while get_pos_y() < ty:
        move(North)
    while get_pos_y() > ty:
        move(South)

def wait_slot():
    w = 0
    while num_drones() >= max_drones():
        if w >= 6:
            return False
        do_a_flip()
        w += 1
    return True

def step(dx, dy):
    if dx == 1:
        move(East)
    elif dx == -1:
        move(West)
    if dy == 1:
        move(North)
    elif dy == -1:
        move(South)

def mine_cell(depth):
    if get_ground_type() != Grounds.Coal:
        return

    dig()

    if depth <= 0:
        return

    expand(depth - 1)

def walk_mine(dx, dy, depth):
    step(dx, dy)
    mine_cell(depth)

def expand(depth):
    if get_ground_type(North) == Grounds.Coal:
        if wait_slot():
            spawn_drone(walk_mine, 0, 1, depth)
        else:
            walk_mine(0, 1, depth)

    if get_ground_type(West) == Grounds.Coal:
        if wait_slot():
            spawn_drone(walk_mine, -1, 0, depth)
        else:
            walk_mine(-1, 0, depth)

    if get_ground_type(East) == Grounds.Coal:
        if wait_slot():
            spawn_drone(walk_mine, 1, 0, depth)
        else:
            walk_mine(1, 0, depth)

    if get_ground_type(South) == Grounds.Coal:
        if wait_slot():
            spawn_drone(walk_mine, 0, -1, depth)
        else:
            walk_mine(0, -1, depth)

def shaft(tx, ty):
    goto(tx, ty)

    base = num_items(Items.Coal)
    d = 0

    while d < MAXSCAN:
        t = get_ground_type()
        if t == Grounds.Coal:
            break
        if t == Grounds.Clay:
            return

        dig()
        d += 1

        # check the global handshake only every 3 digs (each call costs a tick)
        if d % 3 == 0 and num_items(Items.Coal) > base:
            return

    if get_ground_type() == Grounds.Coal:
        mine_cell(DEPTH)

# ---------------- main ----------------
first = 1
round = 0
dx = SIZE // COLS
dy = SIZE // ROWS


def coal(target=-1):
    global first
    global round
    while production.active(Items.Coal, target):

        round += 1
        clear()

        # only the very first round may jump (the game allows it once per execution)
        if first == 1:
            production.jump_once(Unlocks.Coal)
            first = 0

        base = num_items(Items.Coal)

        for r in range(ROWS):
            for c in range(COLS):
                if r == 0 and c == 0:
                    continue
                if num_items(Items.Coal) > base:
                    break
                spawn_drone(shaft, c * dx + dx // 2, r * dy + dy // 2)

        shaft(dx // 2, dy // 2)

        while num_drones() > 1:
            do_a_flip()

        print("round", round, "gained", num_items(Items.Coal) - base)

if __name__ == "__main__":
    coal()
