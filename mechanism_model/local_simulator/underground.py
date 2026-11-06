"""地下柱、16 层区块及塌方；深度向下为正，API 的 z 坐标取负。"""
from collections import deque
from dataclasses import dataclass
import hashlib
import struct

from .catalog import Direction, Grounds, UNDERGROUND
from .noise import OpenSimplexNoise
from .randomness import MAX, MonoRandom, int32


def single(value):
    """复刻 Unity 地层计算中的每次 Single 舍入。"""
    return struct.unpack('<f', struct.pack('<f', value))[0]


@dataclass(frozen=True)
class Ground:
    """一块地层的类型、挖掘硬度和塌方稳定性。"""
    kind: Grounds
    hardness: int
    stability: int


class Underground:
    """按访问生成区块；未实现的已解锁地形明确报错，不替换为普通土。"""

    def __init__(self, world):
        self.world = world
        rng = world.rng['worldGen']
        self.seed = int.from_bytes(hashlib.sha256(rng.bytes(16)).digest()[:4], 'little') & MAX
        self.hardness_noise = OpenSimplexNoise(rng.next())
        self.bamboo_noise = OpenSimplexNoise(world.rng['bamboo'].next())
        self.depths = {(x, y): 0 for y in range(world.size) for x in range(world.width)}
        self.chunks = {}
        self.loop_start = 0

    def ground_at(self, pos, depth=None):
        """读取地层；地表的耕地变化保留原硬度，并采用新地面的稳定性。"""
        current = self.depths[pos]
        depth = current if depth is None else depth
        if depth == 0:
            ground = Ground(Grounds.Grassland, 1, 1)
        else:
            index = depth // 16
            if index not in self.chunks:
                self.chunks[index] = self.generate_chunk(index)
            ground = self.chunks[index][*pos, depth]
        if depth == current and self.world.grounds[pos] != ground.kind:
            kind = self.world.grounds[pos]
            return Ground(kind, ground.hardness, UNDERGROUND['grounds'][kind.name]['stability'])
        return ground

    def generate_chunk(self, index):
        """按资源中的优先级和固定子流生成普通地下地层。"""
        features = UNDERGROUND['features']
        loop_size = 1
        for feature in features:
            unlock = feature['associatedUnlockForGroundLoop']
            allowed = feature['chunkIndexWhitelist']
            if unlock and self.world.unlocks.get(unlock, 0) and allowed:
                last = allowed[0] if feature['onlyIncludeFirstChunkInGroundLoop'] else max(allowed)
                loop_size = max(loop_size, last + 1)
        while index >= self.loop_start + loop_size:
            self.loop_start += loop_size
        relative = index - self.loop_start
        chunk_seed = int32(self.seed + index + 100)
        chunk_rng = MonoRandom(chunk_seed)
        chunk_rng.double()  # DummyGrassland 的概率抽取；它只登记地表占用范围。
        tiles = {}
        for number, feature in enumerate(features, start=2):
            unlock = feature['associatedUnlockForGroundLoop']
            allowed = feature['chunkIndexWhitelist']
            if (not feature['enabled'] or (unlock and not self.world.unlocks.get(unlock, 0))
                    or (allowed and relative not in allowed) or relative in feature['chunkIndexBlacklist']):
                continue
            kind = feature['class_name']
            if kind not in ('HardPatchesFeature', 'LayeredGroundGenFeature', 'AdditiveStabilityNoiseFeature'):
                raise NotImplementedError(f'地下地形尚未实现：{feature["m_Name"]}，区块 {index}')
            chunk_rng.double()
            rng = MonoRandom(int32(chunk_seed + number * 1000))
            if kind == 'HardPatchesFeature':
                self.hard_patches(tiles, index, rng, feature)
            elif kind == 'LayeredGroundGenFeature':
                noise = OpenSimplexNoise(rng.next())
                for x, y in self.depths:
                    for depth in range(index * 16, (index + 1) * 16):
                        if (x, y, depth) not in tiles:
                            tiles[x, y, depth] = self.layered_ground(x, y, depth, noise, feature)
            else:
                noise = OpenSimplexNoise(rng.next())
                for (x, y, depth), ground in list(tiles.items()):
                    addition = int(3 * abs(noise.evaluate(x / 3, y / 3, depth / 3))) - 1
                    tiles[x, y, depth] = Ground(ground.kind, ground.hardness,
                                                       min(4, max(1, ground.stability + addition)))
        for x, y in self.depths:
            for depth in range(index * 16, (index + 1) * 16):
                tiles.setdefault((x, y, depth), Ground(Grounds.Dirt, 1, 1))
        return tiles

    def hard_patches(self, tiles, index, rng, feature):
        """硬块保留原版整数 Next 与 skipTileChance 的比较语义。"""
        horizontal, vertical = feature['periodHorizontal'], feature['periodVertical']
        for x in range(0, self.world.width, horizontal):
            room_x = min(horizontal, self.world.width - x) - 2
            if room_x < 0:
                continue
            for y in range(0, self.world.size, horizontal):
                room_y = min(horizontal, self.world.size - y) - 2
                if room_y < 0:
                    continue
                for z in range(index * 16, (index + 1) * 16, vertical):
                    room_z = min(vertical, (index + 1) * 16 - z) - 2
                    if room_z < 0 or rng.double() < feature['skipAllChance']:
                        continue
                    px, py, pz = x + rng.next(room_x + 1), y + rng.next(room_y + 1), z + rng.next(room_z + 1)
                    for dx in range(2):
                        for dy in range(2):
                            for dz in range(2):
                                if single(rng.next()) >= feature['skipTileChance']:
                                    hardness = int(single(feature['baseHardness'] + single(feature['hardnessIncreaseFrequency'] * (pz + dz - self.loop_start * 16))))
                                    tiles[px + dx, py + dy, pz + dz] = Ground(Grounds.Rock, hardness, min(hardness, 4))

    def layered_ground(self, x, y, depth, noise, feature):
        """普通土与岩层的硬度使用原版 Single 中间值和银行家舍入。"""
        if depth >= 200000000:
            return Ground(Grounds.Bedrock, 1000000000, 1)
        z = depth - self.loop_start * 16
        if 32 <= z < 64:
            return Ground(Grounds.Rock, 2, 3)

        def evaluate(z):
            broad = single(noise.evaluate(single(single(x / 25) + 100), single(single(y / 25) + 100), single(z / 10)))
            b = single(single(z + single(broad * 15)) * feature['hardnessIncreaseFrequency'])
            a = single(single(noise.evaluate(x, y, z)) + 1)
            blend = single(single(single(noise.evaluate(-100, -100, single(z / 15))) * 0.5) + 0.5)
            blend = min(1, max(0, single(single(blend * single(0.66)) + single(0.33))))
            value = single(a + single(single(b - a) * blend))
            step = single(1.2)
            return int(single(round(single(value / step)) * step))

        value = evaluate(z)
        if z >= 64:
            value += 2 - evaluate(64)
        hardness = min(10, max(1, value))
        kind = Grounds.Rock if z >= 16 and hardness in (2, 3) else Grounds.Dirt
        return Ground(kind, hardness, min(4, max(1, value)))

    def clear_column(self, pos, depth):
        """清除指定深度以上的方块与实体；塌方清除不发放物品。"""
        if depth <= self.depths[pos]:
            return
        # 先查询目标块，避免更新柱深度后把旧表层类型误当成新块类型。
        ground = self.ground_at(pos, depth)
        self.depths[pos] = depth
        self.world.grounds[pos] = ground.kind
        self.world.remove(pos)

    def clear_with_caveins(self, pos, depth):
        """依次传播四邻、对角和半径二方环；不跨农田边界传播。"""
        self.clear_column(pos, depth)
        pending = deque()
        neighbors = lambda p: [self.world.neighbor(p, direction) for direction in Direction]
        for target in neighbors(pos):
            if not self.world.in_bounds(target):
                continue
            kind = self.ground_at(target).kind
            if UNDERGROUND['grounds'][kind.name]['autodestroyWhenDugBeside']:
                self.clear_column(target, depth - 1)
            else:
                pending.append(target)
        for dx, dy in ((1, 1), (1, -1), (-1, -1), (-1, 1)):
            target = pos[0] + dx, pos[1] + dy
            if self.world.in_bounds(target):
                pending.append(target)
        directions = ((1, 0), (0, 1), (-1, 0), (0, -1))
        for index, (dx, dy) in enumerate(directions):
            nx, ny = directions[(index + 1) % 4]
            for step in range(4):
                target = pos[0] - 2 * dx - 2 * nx + step * dx, pos[1] - 2 * dy - 2 * ny + step * dy
                if self.world.in_bounds(target) and target[0] != target[1]:
                    pending.append(target)
        while pending:
            target = pending.popleft()
            adjacent = [p for p in neighbors(target) if self.world.in_bounds(p)]
            deepest = max((self.depths[p] for p in adjacent), default=0)
            for z in range(deepest - 1, self.depths[target] - 1, -1):
                if self.ground_at(target, z).stability < deepest - z:
                    self.clear_column(target, z + 1)
                    pending.extend(p for p in adjacent if self.depths[p] < z + 1)
                    break
