from __future__ import annotations
import hashlib
import struct


class DotNetRandom:
    """Compatibility port of legacy C# System.Random.

    This matches the subtractive generator used by classic .NET / Mono,
    which is what TFWR's decompiled code calls via `new Random(seed)`.
    """

    MBIG = 2147483647
    MSEED = 161803398
    MZ = 0

    def __init__(self, seed: int = 0):
        self._seed_array = [0] * 56
        self._inext = 0
        self._inextp = 21
        self.seed(seed)

    def seed(self, seed: int) -> None:
        def _int32(value: int) -> int:
            value &= 0xFFFFFFFF
            if value >= 0x80000000:
                value -= 0x100000000
            return value

        seed = int(seed)
        if seed == -(2**31):
            subtraction = self.MBIG
        else:
            subtraction = abs(seed)
        mj = _int32(self.MSEED - subtraction)
        self._seed_array[55] = mj
        mk = 1
        for i in range(1, 55):
            ii = (21 * i) % 55
            self._seed_array[ii] = mk
            mk = _int32(mj - mk)
            if mk < 0:
                mk += self.MBIG
            mj = self._seed_array[ii]
        for _ in range(4):
            for i in range(1, 56):
                self._seed_array[i] = _int32(self._seed_array[i] - self._seed_array[1 + (i + 30) % 55])
                if self._seed_array[i] < 0:
                    self._seed_array[i] += self.MBIG
        self._inext = 0
        self._inextp = 21

    def getstate(self):
        return ("DotNetRandom", tuple(self._seed_array), self._inext, self._inextp)

    def setstate(self, state) -> None:
        marker, seed_array, inext, inextp = state
        if marker != "DotNetRandom":
            raise ValueError("invalid DotNetRandom state marker")
        if len(seed_array) != 56:
            raise ValueError("invalid DotNetRandom state array length")
        self._seed_array = list(seed_array)
        self._inext = int(inext)
        self._inextp = int(inextp)

    def _internal_sample(self) -> int:
        loc_inext = self._inext + 1
        if loc_inext >= 56:
            loc_inext = 1
        loc_inextp = self._inextp + 1
        if loc_inextp >= 56:
            loc_inextp = 1
        ret_val = self._seed_array[loc_inext] - self._seed_array[loc_inextp]
        if ret_val == self.MBIG:
            ret_val -= 1
        if ret_val < 0:
            ret_val += self.MBIG
        self._seed_array[loc_inext] = ret_val
        self._inext = loc_inext
        self._inextp = loc_inextp
        return ret_val

    def _sample(self) -> float:
        return self._internal_sample() * (1.0 / self.MBIG)

    def _sample_large_range(self) -> float:
        result = self._internal_sample()
        if self._internal_sample() % 2 == 0:
            result = -result
        value = float(result)
        value += self.MBIG - 1
        return value / (2 * self.MBIG - 1)

    def random(self) -> float:
        return self._sample()

    def randbytes(self, n: int) -> bytes:
        n = int(n)
        return bytes(self._internal_sample() % 256 for _ in range(n))

    def randrange(self, start: int, stop: int | None = None) -> int:
        if stop is None:
            stop = int(start)
            start = 0
        start = int(start)
        stop = int(stop)
        if stop <= start:
            raise ValueError("empty range for randrange()")
        range_size = stop - start
        if range_size <= self.MBIG:
            return int(self._sample() * range_size) + start
        return int(self._sample_large_range() * range_size) + start

    def randint(self, a: int, b: int) -> int:
        return self.randrange(int(a), int(b) + 1)

    def just_sha256_it(self) -> int:
        """Helper.JustSha256It implementation from Utils.dll
        
        Generates a derived seed by:
        1. Getting 16 random bytes from this RNG
        2. Computing SHA256 hash
        3. Taking first 4 bytes as int32
        4. Masking to ensure positive value
        """
        buffer = self.randbytes(16)
        hash_bytes = hashlib.sha256(buffer).digest()
        seed = struct.unpack('<i', hash_bytes[:4])[0]
        return seed & 0x7FFFFFFF
