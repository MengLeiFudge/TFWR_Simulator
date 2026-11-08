from __builtins__ import *
import mining


def block(target=-1):
    mining.mine(Items.Block, None, 16, target=target)


if __name__ == "__main__":
    block()
