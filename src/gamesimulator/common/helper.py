from __future__ import annotations

import hashlib


def world_size_scale(num_expand_upgrades: int) -> int:
    if num_expand_upgrades <= 0:
        return 1
    if num_expand_upgrades == 1:
        return 2
    if num_expand_upgrades == 2:
        return 3
    if num_expand_upgrades == 3:
        return 4
    if num_expand_upgrades == 4:
        return 6
    if num_expand_upgrades == 5:
        return 8
    if num_expand_upgrades == 6:
        return 12
    if num_expand_upgrades == 7:
        return 16
    if num_expand_upgrades == 8:
        return 22
    return 32


def num_drones(num_megafarm_upgrades: int) -> int:
    return 1 << num_megafarm_upgrades


def just_sha256_it(random_source) -> int:
    """Port of Helper.JustSha256It.

    The C# code asks the parent RNG for 16 bytes, hashes them with SHA256,
    reads the first 4 bytes as a little-endian signed int, then clears the sign
    bit.
    """

    try:
        buffer = random_source.randbytes(16)
    except AttributeError:
        buffer = bytes(random_source.getrandbits(8) for _ in range(16))
    digest = hashlib.sha256(buffer).digest()
    value = int.from_bytes(digest[:4], byteorder="little", signed=True)
    return value & 0x7FFFFFFF
