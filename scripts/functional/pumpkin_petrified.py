from __builtins__ import *
import mining


def pumpkin_petrified(target=-1):
    mining.mine(Items.Pumpkin, Grounds.Petrified_Pumpkin, 64, Unlocks.Petrified_Pumpkins, target)


if __name__ == "__main__":
    pumpkin_petrified()
