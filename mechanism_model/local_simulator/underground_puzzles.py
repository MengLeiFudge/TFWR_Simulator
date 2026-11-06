"""金字塔的几何完成条件与奖励，不承担普通地形生成。"""
from .catalog import Entities, Grounds


PYRAMID_GROUNDS = (Grounds.Sand, Grounds.Block_Red, Grounds.Block_Green, Grounds.Block_Blue)


def check_pyramid(underground, pos, depth):
    """仅检查触发位置所属的一座金字塔；每列高度和整座材料类别必须一致。"""
    world = underground.world
    for pyramid in list(underground.pyramids):
        px, py, bottom, size = pyramid
        x, y = pos[0] - px, pos[1] - py
        if not (0 <= x < size and 0 <= y < size
                and bottom - 1 - min(x, y, size - 1 - x, size - 1 - y) < depth <= bottom):
            continue
        material = None
        for y in range(size):
            for x in range(size):
                point = px + x, py + y
                top = bottom - min(x, y, size - 1 - x, size - 1 - y)
                if underground.depths[point] != top:
                    return
                for z in range(bottom, top - 1, -1):
                    kind = underground.ground_at(point, z).kind
                    if kind not in PYRAMID_GROUNDS:
                        return
                    category = kind == Grounds.Sand
                    if material is not None and material != category:
                        return
                    material = category
        underground.pyramids.remove(pyramid)
        for x in range(px, px + size):
            for y in range(py, py + size):
                underground.clear_column((x, y), bottom + 1)
        crop = world.set_entity((px + size // 2, py + size // 2), Entities.Sunflower)
        crop.pyramid_yield = size * size * max(1, 1 << max(0, world.unlocks['pyramid'] - 1)) * 0.25
        if crop.timer is not None:
            crop.timer.stopped = True
        crop.timer = None
        world.mature(crop)
        return
