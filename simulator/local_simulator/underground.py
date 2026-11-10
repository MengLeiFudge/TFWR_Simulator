"""地下柱、16 层区块及塌方；深度向下为正，API 的 z 坐标取负。"""
from collections import deque
import hashlib

from .catalog import Direction, Grounds, UNDERGROUND
from .noise import OpenSimplexNoise
from .randomness import MAX, MonoRandom, int32


from .underground_types import Ground, Bounds, single
from .underground_features import Features
from .underground_explosives import Sweeper
from .underground_treasure import TreasureMaps


class Underground:
    """按访问生成区块；未实现的已解锁地形明确报错，不替换为普通土。"""

    def __init__(self, world, starting_chunk=0, jump_targets=()):
        self.world = world
        self.jump_targets = jump_targets
        self.starting_chunk = starting_chunk
        self.max_depth = starting_chunk * 16
        self.topology_revision = 0
        rng = world.rng['worldGen']
        self.seed = int.from_bytes(hashlib.sha256(rng.bytes(16)).digest()[:4], 'little') & MAX
        self.hardness_noise = OpenSimplexNoise(rng.next())
        self.bamboo_noise = OpenSimplexNoise(world.rng['bamboo'].next())
        self.depths = {(x, y): starting_chunk * 16 for y in range(world.size) for x in range(world.width)}
        self.chunks = {}
        self.features = {}
        self.ore_cache = {}
        self.placed = {}
        self.pyramids = []
        self.removed = set()
        self.sweeper = Sweeper(self)
        self.treasure = TreasureMaps(self)
        self.loop_start = 0

    def ground_at(self, pos, depth=None):
        """读取地层；地表的耕地变化保留原硬度，并采用新地面的稳定性。"""
        current = self.depths[pos]
        depth = current if depth is None else depth
        if (*pos, depth) in self.placed:
            ground = self.placed[*pos, depth]
        elif depth < 0 or (depth == 0 and not (self.world.leaderboard and self.world.leaderboard['pretendedChunkDepths'] and self.world.leaderboard['pretendedChunkDepths'][0])):
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
        profile = self.world.leaderboard
        selected_features = profile['whitelistedGroundFeatureUnlocks'] if profile else []
        if selected_features:
            loop_size = len(selected_features)
        while index >= self.loop_start + loop_size:
            self.loop_start += loop_size
        relative = index - self.loop_start
        selected = selected_features[relative] if selected_features else None
        filter_index = profile['pretendedFeatureChunks'][relative] if selected else relative
        pretended_depth = None
        chunk_seed = int32(self.seed + index + 100)
        chunk_rng = MonoRandom(chunk_seed)
        chunk_rng.double()  # DummyGrassland 的概率抽取；它只登记地表占用范围。
        tiles = {}
        previous = [('DummyGrasslandFeature', Bounds((0, 0, 0), (self.world.width, self.world.size, 1)))] if index == 0 else []
        generators = {'SpecialSoilsFeature': 'special_soils', 'OreVeinFeature': 'iron',
                      'QuartzVeinFeature': 'quartz', 'PetrifiedPumpkinsFeature': 'petrified',
                      'MushroomFeature': 'mushrooms', 'PyramidFeature': 'pyramid', 'SweeperStratumFeature': 'sweeper',
                      'TreasureMapFeature': 'treasure_map'}
        for number, feature in enumerate(features, start=2):
            unlock = feature['associatedUnlockForGroundLoop']
            allowed = feature['chunkIndexWhitelist']
            forced = selected == feature['m_Name']
            if not feature['enabled']:
                continue
            if selected:
                if unlock and not forced:
                    continue
            elif unlock and not self.world.unlocks.get(unlock, 0):
                continue
            if not forced and ((allowed and filter_index not in allowed) or filter_index in feature['chunkIndexBlacklist']):
                continue
            if forced and profile['pretendedChunkDepths']:
                pretended_depth = profile['pretendedChunkDepths'][relative]
            kind = feature['class_name']
            if kind == 'QuartzFeature':
                kind = 'QuartzVeinFeature'
            probability = feature.get('probability', 1)
            if kind == 'PetrifiedPumpkinsFeature' and self.world.width <= 3 and self.world.size <= 3:
                probability = 0
            if kind in ('SweeperStratumFeature', 'TreasureMapFeature') and self.world.width <= 3 and self.world.size <= 3:
                probability = 0
            if kind == 'PyramidFeature' and self.world.width <= 5 and self.world.size <= 5:
                probability = 0
            if 'PyramidFeature' in self.jump_targets and kind in ('MushroomFeature', 'TreasureMapFeature'):
                continue
            if not forced and kind not in self.jump_targets and probability < chunk_rng.double():
                continue
            rng = MonoRandom(int32(chunk_seed + number * 1000))
            boxes = []
            if kind in generators:
                context = Features(self, tiles, index, rng, feature, previous)
                boxes = getattr(context, generators[kind])()
            elif kind == 'HardPatchesFeature':
                boxes = self.hard_patches(tiles, index, rng, feature)
            elif kind == 'ClayFeature':
                boxes = self.clay(tiles, index, rng, feature, previous)
            elif kind == 'CoalFeature':
                boxes = self.coal(tiles, index, rng, feature)
            elif kind == 'LayeredGroundGenFeature':
                noise = OpenSimplexNoise(rng.next())
                for x, y in self.depths:
                    for depth in range(index * 16, (index + 1) * 16):
                        if (x, y, depth) not in tiles:
                            tiles[x, y, depth] = self.layered_ground(x, y, depth, noise, feature, pretended_depth)
            elif kind == 'AdditiveStabilityNoiseFeature':
                noise = OpenSimplexNoise(rng.next())
                for (x, y, depth), ground in list(tiles.items()):
                    addition = int(3 * abs(noise.evaluate(x / 3, y / 3, depth / 3))) - 1
                    tiles[x, y, depth] = Ground(ground.kind, ground.hardness,
                                                       min(4, max(1, ground.stability + addition)), ground.color, ground.stratum)
            else:
                raise NotImplementedError(f'地下地形尚未实现：{feature["m_Name"]}，区块 {index}')
            previous.extend((kind, box) for box in boxes)
        self.features[index] = previous
        for x, y in self.depths:
            for depth in range(index * 16, (index + 1) * 16):
                tiles.setdefault((x, y, depth), Ground(Grounds.Dirt, 1, 1))
        return tiles

    def clay(self, tiles, index, rng, feature, previous):
        """按二维噪声生成两层粘土，上方填土，下方填岩。"""
        noise = OpenSimplexNoise(rng.next())
        start = index * 16 + feature['startOffset'] + rng.next(feature['randomStartOffsetMin'], feature['randomStartOffsetMax'])
        box = Bounds((0, 0, start), (self.world.width, self.world.size, 16))
        if any(box.overlaps(old) for _, old in previous):
            return []
        height = index * 16 + 15 - start
        scale = feature['noiseSamplingScale']
        for x, y in self.depths:
            surface = start + int((noise.evaluate(single(x * scale), single(y * scale)) + 1) * 0.5 * height * feature['noiseHeightMultiplier'])
            for z in range(index * 16, (index + 1) * 16):
                kind = Grounds.Dirt if z < surface else Grounds.Clay if z < surface + 2 else Grounds.Rock
                data = UNDERGROUND['grounds'][kind.name]
                tiles[x, y, z] = Ground(kind, data['maxHardness'], data['stability'])
        return [box]

    def coal(self, tiles, index, rng, feature):
        """随机煤层的队列允许重复入队，重复出队也计入原版尺寸预算。"""
        start = max(index * 16, self.loop_start * 16 + feature['loopRelativeDepthStart'])
        end = min((index + 1) * 16, self.loop_start * 16 + feature['loopRelativeDepthEnd'])
        layers = sorted(range(start, end), key=lambda _: rng.next())
        count = feature['sheetCountPerUnlock'][self.world.unlocks['coal']]
        data = UNDERGROUND['grounds']['Coal']
        ground = Ground(Grounds.Coal, data['maxHardness'], data['stability'])
        limit = int(single(self.world.width * self.world.width * single(0.8)))
        boxes = []
        for depth in layers[:count]:
            pending = deque([(rng.next(self.world.width), rng.next(self.world.size))])
            visited = set()
            used = 0
            while pending and used < limit:
                pos = pending.popleft()
                visited.add(pos)
                tiles[*pos, depth] = ground
                for direction in Direction:
                    neighbor = self.world.neighbor(pos, direction)
                    if self.world.in_bounds(neighbor) and neighbor not in visited:
                        pending.append(neighbor)
                for dx, dy in ((1, 1), (1, -1), (-1, -1), (-1, 1)):
                    neighbor = pos[0] + dx, pos[1] + dy
                    if (self.world.in_bounds(neighbor) and rng.double() > feature['veinCornerSkipChance']
                            and neighbor not in visited):
                        pending.append(neighbor)
                used += 1
            boxes.append(Bounds.enclosing((*pos, depth) for pos in visited))
        return boxes

    def hard_patches(self, tiles, index, rng, feature):
        """硬块保留原版整数 Next 与 skipTileChance 的比较语义。"""
        boxes = []
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
                    boxes.append(Bounds((px, py, pz), (px + 2, py + 2, pz + 2)))
        return boxes

    def layered_ground(self, x, y, depth, noise, feature, pretended_depth=None):
        """普通土与岩层的硬度使用原版 Single 中间值和银行家舍入。"""
        if depth >= 200000000:
            return Ground(Grounds.Bedrock, 1000000000, 1)
        z = depth - self.loop_start * 16 if pretended_depth is None else depth % 16 + pretended_depth
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

    def closest_ore(self, kind):
        """按区块和矿脉缓存顺序寻找32格内仍存在的矿石；相等距离保留先遇到者。"""
        pos = self.world.pos
        depth = self.depths[pos]
        best, distance = None, float('inf')
        for index in range(max(0, depth // 16 - 2), depth // 16 + 3):
            if index not in self.chunks:
                self.chunks[index] = self.generate_chunk(index)
            for x, y, z in self.ore_cache.get(index, {}).get(kind.name.lower(), []):
                if z < self.depths[x, y] or self.ground_at((x, y), z).kind != kind:
                    continue
                current = (abs(x - pos[0]) + abs(y - pos[1]) + z - self.depths[x, y] if kind == Grounds.Iron
                           else single(((x - pos[0]) ** 2 + (y - pos[1]) ** 2 + (z - depth) ** 2) ** 0.5))
                if current <= 32 and current < distance:
                    best, distance = (x, y, z), current
        return best, distance

    def present(self, point):
        """柱顶以下默认实心，控制器可暂时移除顶块而尚未推进柱深度。"""
        return point[2] >= self.depths[point[:2]] and point not in self.removed

    def place(self, pos, block):
        """放置到柱顶；沙子需石灰岩或完整八邻沙层支撑。"""
        below = self.depths[pos]
        supported = True
        if block.kind == Grounds.Sand:
            base = self.ground_at(pos).kind
            supported = base == Grounds.Limestone
            if base == Grounds.Sand:
                supported = all(self.world.in_bounds(p) and self.depths[p] <= below
                                and self.ground_at(p, below).kind in (Grounds.Sand, Grounds.Limestone)
                                for p in ((pos[0] + dx, pos[1] + dy) for dx in (-1, 0, 1)
                                          for dy in (-1, 0, 1) if dx or dy))
        self.world.remove(pos, regrow=False)
        if supported:
            self.removed.discard((*pos, below - 1))
            self.placed[*pos, below - 1] = block
            self.depths[pos] = below - 1
            self.topology_revision += 1
            self.world.grounds[pos] = block.kind
        return supported

    def push(self, source, target):
        """移动表层方块；同色蘑菇合并只清柱，不触发塌方。"""
        block = self.ground_at(source)
        target_depth = self.depths[target] - 1
        below = self.ground_at(target)
        self.removed.discard((*target, target_depth))
        self.placed[*target, target_depth] = block
        next_source = self.ground_at(source, self.depths[source] + 1)
        self.topology_revision += 1
        self.depths[source] += 1
        self.depths[target] = target_depth
        self.world.grounds[source] = next_source.kind
        self.world.grounds[target] = block.kind
        self.world.remove(source, regrow=False)
        if block.kind == Grounds.Mushroom and below.kind == Grounds.Mushroom and block.color == below.color:
            self.clear_column(target, target_depth + 2)
            return max(1, 1 << max(0, self.world.unlocks['mushrooms'] - 1))
        return 0

    def clear_column(self, pos, depth):
        """清除指定深度以上的方块与实体；塌方清除不发放物品。"""
        if depth <= self.depths[pos]:
            return
        # 先查询目标块，避免更新柱深度后把旧表层类型误当成新块类型。
        ground = self.ground_at(pos, depth)
        self.depths[pos] = depth
        self.topology_revision += 1
        self.max_depth = max(self.max_depth, depth)
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
                # 原版比较相对开挖点的偏移，不能按世界坐标排除主对角线。
                if self.world.in_bounds(target) and target[0] - pos[0] != target[1] - pos[1]:
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
