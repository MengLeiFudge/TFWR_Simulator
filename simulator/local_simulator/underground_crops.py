"""地下作物的分阶段生长与无人机交互；通用成熟计时仍由 FarmWorld 持有。"""
from .catalog import Items, UNDERGROUND


class Bamboo:
    """一棵竹子的高度和三处花节；无人机阻挡与切割不会重新抽花节。"""

    def __init__(self, world, crop):
        self.world, self.crop = world, crop
        self.height = 1
        self.next_flower = 0
        self.flowers = []
        x, y = crop.pos
        extra = round(world.underground.bamboo_noise.evaluate(x / 2 + 97, y / 2 + 97) / 2 + 0.5)
        height = 1
        for index in range(3):
            increment = world.rng['bamboo'].next(2, 5) + extra
            height += increment if index == 0 else max(3, increment)
            self.flowers.append(height)
        crop.number = self.flowers[0] - 1

    def grow(self, ignore_drone=None):
        """只有本阶段成熟、没有无人机阻挡且尚未触及花节时才继续生长。"""
        world, crop = self.world, self.crop
        if not crop.grown or self.height >= self.flowers[-1] or self.height == self.flowers[self.next_flower]:
            return
        if any(drone != ignore_drone and pos == crop.pos and world.hover_heights.get(drone, 1) <= self.height
               for drone, pos in world.drone_positions.items()):
            return
        self.height += 1
        world.restart_growth(crop)

    def drops(self, count):
        """切下的高度平方乘作物科技和地面倍率。"""
        world, crop = self.world, self.crop
        return count * count * world.yield_factor(crop.kind) * UNDERGROUND['grounds'][world.grounds[crop.pos].name]['yieldMultiplierForGrowables']

    def cut(self, height, collect=True):
        """切割至进入格子的飞行高度；切花后保留同一株的后续花节。"""
        if height >= self.height:
            return
        world, crop = self.world, self.crop
        if collect:
            world.add_item(Items.Bamboo, self.drops(self.height - height))
        if height == 0:
            world.remove(crop.pos)
            return
        if height >= self.flowers[self.next_flower] - 1:
            self.next_flower = min(self.next_flower + 1, 2)
        else:
            self.next_flower = 0
            while self.next_flower < 2 and height >= self.flowers[self.next_flower]:
                self.next_flower += 1
        self.height = height
        crop.number = self.flowers[self.next_flower] - 1
        if not crop.grown:
            world.mature(crop)
