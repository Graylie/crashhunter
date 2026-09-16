"""Deterministic seed corpus and byte-level mutations."""

from __future__ import annotations

import random


SEEDS = (
    b"",
    b"A",
    b"0",
    b"CRASH",
    b"OVERFLOW",
    b"../" * 8,
    b"\x00",
    b"A" * 64,
    b"A" * 4096,
    b"{\"id\": -1, \"name\": \"test\"}",
    b"%s%s%s%s%n",
)


class InputGenerator:
    def __init__(self, seed: int) -> None:
        self.random = random.Random(seed)

    def cases(self, count: int):
        for index in range(count):
            if index < len(SEEDS):
                yield SEEDS[index]
            else:
                yield self._mutate(self.random.choice(SEEDS))

    def _mutate(self, source: bytes) -> bytes:
        data = bytearray(source)
        action = self.random.choice(("flip", "insert", "repeat", "replace"))
        if action == "flip" and data:
            at = self.random.randrange(len(data))
            data[at] ^= 1 << self.random.randrange(8)
        elif action == "repeat":
            data *= self.random.randint(2, 8)
        elif action == "replace" and data:
            at = self.random.randrange(len(data))
            data[at] = self.random.randrange(256)
        else:
            at = self.random.randrange(len(data) + 1)
            data[at:at] = bytes(self.random.randrange(256) for _ in range(self.random.randint(1, 16)))
        return bytes(data[:65536])
