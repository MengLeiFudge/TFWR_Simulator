"""原版 Mono System.Random 及 Simulation 的八流派生。"""

import hashlib

MAX = 2147483647
STREAM_NAMES = ('various', 'maze', 'snake', 'cactus', 'sunflower', 'pumpkin', 'poly', 'random')


def int32(value: int) -> int:
    return ((value + 2147483648) & 0xffffffff) - 2147483648


class MonoRandom:
    """显式 Int32 seed 的减法发生器；保留 Mono 的 unchecked 溢出行为。"""

    def __init__(self, seed: int):
        if not -2147483648 <= seed <= MAX:
            raise ValueError('seed 必须在 Int32 范围内')
        self.state = [0] * 56
        mj = 161803398 - (MAX if seed == -2147483648 else abs(seed))
        self.state[55] = mj
        mk = 1
        for i in range(1, 55):
            index = (21 * i) % 55
            self.state[index] = mk
            mk = int32(mj - mk)
            if mk < 0:
                mk = int32(mk + MAX)
            mj = self.state[index]
        for _ in range(4):
            for i in range(1, 56):
                self.state[i] = int32(self.state[i] - self.state[1 + (i + 30) % 55])
                if self.state[i] < 0:
                    self.state[i] = int32(self.state[i] + MAX)
        self.a, self.b = 0, 21
        self.draws = 0

    def sample_int(self) -> int:
        self.a = self.a % 55 + 1
        self.b = self.b % 55 + 1
        value = int32(self.state[self.a] - self.state[self.b])
        if value == MAX:
            value -= 1
        if value < 0:
            value += MAX
        self.state[self.a] = value
        self.draws += 1
        return value

    def double(self) -> float:
        return self.sample_int() * 4.656612875245797e-10

    def next(self, minimum: int | None = None, maximum: int | None = None) -> int:
        """Next()/Next(max)/Next(min,max)；零宽范围仍消耗一次抽取。"""
        if minimum is None:
            return self.sample_int()
        if maximum is None:
            minimum, maximum = 0, minimum
        if not -2147483648 <= minimum <= maximum <= MAX:
            raise ValueError('无效的 Int32 随机范围')
        width = maximum - minimum
        if width <= MAX:
            return int(self.double() * width) + minimum
        value = self.sample_int()
        if self.sample_int() % 2 == 0:
            value = -value
        return int(((value + 2147483646.0) / 4294967293.0) * width) + minimum

    def bytes(self, count: int) -> bytes:
        return bytes(self.sample_int() & 255 for _ in range(count))


def stream_seeds(seed: int) -> dict[str, int]:
    if not 0 <= seed <= MAX:
        raise ValueError('可重放的游戏 seed 必须在 0..2147483647 内')
    master = MonoRandom(seed)
    return {
        name: int.from_bytes(hashlib.sha256(master.bytes(16)).digest()[:4], 'little') & MAX
        for name in STREAM_NAMES
    }
