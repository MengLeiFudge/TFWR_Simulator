# 淘汰候选归档：lb_dinosaur | 原实验路径 .codex/bilibili-improvement-20261112/adapt_dinosaur.py
"""把已读MIT区域算法适配为独立功能和排行榜入口，保留原始源供对照。"""
from pathlib import Path
import ast
import shutil

ROOT = Path(__file__).resolve().parents[2]
WORK = Path(__file__).resolve().parent
source = ast.parse((WORK / 'original-dinosaur/snaky2.py').read_text())
names = {'LtoH': 'cycle_index', 'is_in_area': 'in_region', 'snaky_move': 'region_step',
         'snaky_quick_move': 'reach_in_region', 'quick_getout': 'leave_region',
         'eat_apple': 'collect_in_region', 'snaky2': 'production_cycle',
         'snaky2_size': 'farm_size', 'reverse': 'REVERSE'}


class Rename(ast.NodeTransformer):
    def visit_Name(self, node):
        node.id = names.get(node.id, node.id)
        return node

    def visit_FunctionDef(self, node):
        node.name = names.get(node.name, node.name)
        return self.generic_visit(node)


source = Rename().visit(source)
functions = [node for node in source.body if isinstance(node, ast.FunctionDef) and node.name != 'main']
for fn in functions:
    if fn.name in ('cycle_index', 'in_region'):
        for node in ast.walk(fn):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == 'get_world_size':
                node.value = ast.Name(id='farm_size', ctx=ast.Load())
    if fn.name == 'reach_in_region':
        for node in fn.body:
            if isinstance(node, ast.While):
                node.test = ast.parse('get_time() < cycle_deadline', mode='eval').body
        fn.body.append(ast.parse('return None').body[0])
    if fn.name == 'collect_in_region':
        fn.body.insert(0, ast.parse('if get_time() >= cycle_deadline:\n    return target, cnt').body[0])
        first = next(i for i,n in enumerate(fn.body) if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='w_g' for x in ast.walk(n.targets[0])))
        last = next(i for i,n in enumerate(fn.body) if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='area_ins')
        # 此段只计算未使用的宽度；region_step的模拟分支没有移动或其他状态写入。
        del fn.body[first:last]
    if fn.name == 'production_cycle':
        fn.args = ast.arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[])
        # 普通全科技田在clear后确定大小；整轮不再改变地图，供所有区域函数复用。
        fn.body[1:2] = ast.parse('size = get_world_size()\nfarm_size = size\ncycle_deadline = get_time() + 1200').body
        fn.body[0:0] = ast.parse('global farm_size\nglobal cycle_deadline').body
        outer = next(n for n in fn.body if isinstance(n, ast.While))
        early = next(n for n in outer.body if isinstance(n, ast.While))
        early.test = ast.parse('get_time() < cycle_deadline', mode='eval').body
        half = next(n for n in early.body if isinstance(n, ast.If) and ast.unparse(n.test)=='cnt >= turn_point')
        half.body = ast.parse('quick_print("dinosaur_finish", cnt, get_time())\nwhile move(main_move[id % A]):\n    id += 1\nbreak').body
        # 外层只执行一次就return，直接展开为单个生产周期。
        at = fn.body.index(outer)
        fn.body[at:at+1] = outer.body
        for node in fn.body:
            if isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name) and node.value.func.id=='change_hat':
                if isinstance(node.value.args[0],ast.Attribute) and node.value.args[0].attr=='Straw_Hat':node.value.args[0].attr='Brown_Hat'
        if isinstance(fn.body[-1],ast.Return):fn.body[-1]=ast.parse('return').body[0]

functions = ast.fix_missing_locations(ast.Module(body=functions, type_ignores=[]))
explanations = {'cycle_index':'主回路编号只用本轮固定田尺寸，避免每次坐标换算重新读取世界。',
                'in_region':'判断目标是否仍在区域的前方，左右转向随区域旋转。',
                'region_step':'返回区域蛇形方向；给出模拟坐标时只计算，不移动。',
                'reach_in_region':'在当前安全矩形内沿剪枝路线到目标，返回最后转折点；超时交回上层。',
                'leave_region':'按区域出口恢复父区域路线，避免任意短路破坏身体形状。',
                'collect_in_region':'沿当前矩形吃果，递归进入可恢复子区域，返回新目标与观测计数。',
                'production_cycle':'一轮前半采用递归区域，后半按预建主回路填满；退出时换帽真实结算。'}
common = 'REVERSE = {East: West, West: East, North: South, South: North}\nfarm_size = 32\ncycle_deadline = 0\n\n\n'
common += '\n\n\n'.join('# '+explanations[fn.name]+'\n'+ast.unparse(fn) for fn in functions.body) + '\n'
notice = '# Copyright (c) [2026] [lywlucas]; MIT许可见lywlucas_LICENSE.txt。\n# 来源：https://github.com/lywlucas/The_Farmer_was_Replaced/tree/99091a59855da87276573fe37d1bb7e3854704de\n'
functional = '''from __builtins__ import *
import production
'''+notice+'''

def bone_dinosaur(target=-1):
    # 有限库存也先完成整条蛇；入库和回收后才判断是否开始下一轮。
    cycles = 0
    while production.active(Items.Bone, target):
        before = num_items(Items.Bone)
        began = get_time()
        production_cycle()
        gain = num_items(Items.Bone) - before
        expected = (farm_size * farm_size - 1) ** 2 * 2 ** max(0, num_unlocked(Unlocks.Dinosaurs) - 1)
        cycles += 1
        quick_print("dinosaur_cycle", cycles, gain, get_time() - began, get_time())
        if gain < expected:
            quick_print("dinosaur_failed", "incomplete_cycle", gain, expected)
            return


'''+common+'''\n
if __name__ == "__main__":
    bone_dinosaur()
'''
leaderboard = '''from __builtins__ import *
'''+notice+'''

def lb_dinosaur():
    before = num_items(Items.Bone)
    began = get_time()
    production_cycle()
    gain = num_items(Items.Bone) - before
    expected = (farm_size * farm_size - 1) ** 2 * 2 ** max(0, num_unlocked(Unlocks.Dinosaurs) - 1)
    quick_print("dinosaur_cycle", gain, get_time() - began)
    if gain < expected:
        quick_print("dinosaur_failed", "incomplete_cycle", gain, expected)


'''+common+'''\n
if __name__ == "__main__":
    lb_dinosaur()
'''
for name, code, file in [('adapted-functional', functional, 'bone_dinosaur.py'), ('adapted-leaderboard', leaderboard, 'lb_dinosaur.py')]:
    folder = WORK / name
    folder.mkdir(exist_ok=False)
    (folder / file).write_text(code)
    shutil.copy2(WORK / 'original-dinosaur/LICENSE', folder / 'lywlucas_LICENSE.txt')
    if name=='adapted-functional':shutil.copy2(WORK/'baseline/production.py',folder/'production.py')
    print(name,len(code.splitlines()),flush=True)
