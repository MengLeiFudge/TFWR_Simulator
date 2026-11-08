from __builtins__ import *
import mining


def iron(target=-1):
    mining.mine(Items.Iron, Grounds.Iron, 64, Unlocks.Iron, target)


if __name__ == "__main__":
    iron()
