from __builtins__ import *
# 妙手回春：肥料使胡萝卜感染，再用怪异物质治愈同一株。
MAX_GAME_SECONDS = 300


def healer():
    clear()
    till()
    if not plant(Entities.Carrot) or not use_item(Items.Fertilizer):
        quick_print("种植或感染失败；请准备胡萝卜种植材料和肥料。")
        return
    if use_item(Items.Weird_Substance):
        quick_print("已用怪异物质治愈感染的胡萝卜。")
    else:
        quick_print("治愈失败；请准备怪异物质。")


if __name__ == "__main__":
    healer()
