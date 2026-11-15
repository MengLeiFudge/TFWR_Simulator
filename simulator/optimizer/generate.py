"""按已记录配方生成游戏脚本，只转换显式标记的固定循环和环绕路径表。"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from builtins import str
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def wrap_tables(size: int, stride: int) -> tuple[list[int], list[list[str]]]:
    if size < 2 or size > 32 or stride < 2 * size - 1:
        raise ValueError("环绕路径表要求2..32格，编码步长至少为2*size-1")
    span = (size - 1) * (stride + 1)
    distances: list[int] = []
    paths: list[list[str]] = []
    for delta in range(-span, span + 1):
        dx = (delta + size - 1) % stride - (size - 1)
        dy = (delta - dx) // stride
        route: list[str] = []
        if abs(dx) >= size or abs(dy) >= size:
            distances.append(99)
            paths.append(route)
            continue
        for amount, positive, negative in [(dx % size, "East", "West"), (dy % size, "North", "South")]:
            if amount <= size // 2:
                route.extend([positive] * amount)
            else:
                route.extend([negative] * (size - amount))
        distances.append(len(route))
        paths.append(route)
    return distances, paths


def unsupported_control(loop: ast.For) -> bool:
    pending: list[tuple[ast.AST, int]] = [(child, 0) for child in loop.body]
    while pending:
        node, depth = pending.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return True
        if isinstance(node, (ast.Break, ast.Continue)) and depth == 0:
            return True
        if isinstance(node, (ast.For, ast.While)):
            pending.extend((child, depth + 1) for child in node.body)
            pending.extend((child, depth) for child in node.orelse)
        else:
            pending.extend((child, depth) for child in ast.iter_child_nodes(node))
    return False


def render(template: str, transforms: dict) -> str:
    lines = template.splitlines()
    if set(transforms) - {"unroll", "wrap_paths"}:
        raise ValueError("配方含未知转换项")
    changes: list[tuple[int, int, list[str]]] = []
    tree = ast.parse(template)
    if transforms.get("unroll", False):
        if any((isinstance(node, ast.Name) and node.id == "range" and isinstance(node.ctx, ast.Store)) or (isinstance(node, ast.arg) and node.arg == "range") or (isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == "range") for node in ast.walk(tree)):
            raise ValueError("固定展开不允许重绑定range")
        for node in ast.walk(tree):
            if not isinstance(node, ast.For) or node.lineno < 2 or lines[node.lineno - 2].strip() != "#@unroll":
                continue
            call = node.iter
            if not isinstance(node.target, ast.Name) or not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name) or call.func.id != "range" or call.keywords:
                raise ValueError(f"第{node.lineno}行只支持普通变量和常量range")
            values = [ast.literal_eval(arg) for arg in call.args]
            if any(type(value) is not int for value in values) or not 1 <= len(values) <= 3:
                raise ValueError(f"第{node.lineno}行range参数必须是整数常量")
            iterations = range(*values)
            if not iterations or len(iterations) > 64 or node.orelse or unsupported_control(node):
                raise ValueError(f"第{node.lineno}行无法证明固定展开等价，或超过64次")
            if node.end_lineno is None:
                raise ValueError("无法确定循环源码范围")
            indent = " " * node.col_offset
            body = lines[node.lineno:node.end_lineno]
            expanded: list[str] = []
            for value in iterations:
                expanded.append(f"{indent}{node.target.id} = {value}")
                for line in body:
                    expanded.append(line[4:] if line.strip() else "")
            changes.append((node.lineno - 2, node.end_lineno, expanded))
    table = transforms.get("wrap_paths")
    if table:
        marker = f"#@wrap_paths {table['size']} {table['stride']}"
        found = [i for i, line in enumerate(lines) if line.strip() == marker]
        if len(found) != 1:
            raise ValueError("母版须有唯一匹配的wrap_paths标记")
        start = found[0]
        if lines[start + 1].strip() != "SUN_DISTANCE, SUN_PATHS = sunflower_tables()":
            raise ValueError("环绕表标记后须为sunflower_tables初始化")
        distances, paths = wrap_tables(table["size"], table["stride"])
        literals = ["SUN_DISTANCE = " + repr(distances), "SUN_PATHS = ["]
        literals.extend("    [" + ", ".join(path) + "]," for path in paths)
        literals.append("]")
        changes.append((start, start + 2, literals))
    previous_end = -1
    for start, end, _ in sorted(changes):
        if start < previous_end:
            raise ValueError("转换标记范围重叠")
        previous_end = end
    for start, end, replacement in sorted(changes, reverse=True):
        lines[start:end] = replacement
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("recipe", type=Path)
    parser.add_argument("--check", action="store_true", help="只核对产物及三个源码指纹，不写文件")
    args = parser.parse_args()
    recipe_path = args.recipe.resolve()
    recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
    template_path = (ROOT / recipe["template"]).resolve()
    output_path = (ROOT / recipe["output"]).resolve()
    if not template_path.is_relative_to(ROOT) or not output_path.is_relative_to(ROOT) or output_path == template_path:
        raise ValueError("母版和独立产物必须位于仓库内")
    source = template_path.read_text(encoding="utf-8")
    generated = render(source, recipe.get("transforms", {}))
    lines = generated.splitlines()
    if lines[0] != "from __builtins__ import *" or not lines[1].startswith("# 完整轮时间："):
        raise ValueError("母版前两行必须为游戏内置导入和完整轮时间状态")
    lines[2:2] = [f"# 生成自：{template_path.relative_to(ROOT).as_posix()}", f"# 生成配置：{recipe_path.relative_to(ROOT).as_posix()}", "# 修改策略请编辑母版并重新生成，勿直接修改本文件。"]
    data = ("\n".join(lines) + "\n").encode("utf-8")
    fingerprints = {"template_sha256": digest(template_path.read_bytes()), "generator_sha256": digest(Path(__file__).read_bytes()), "output_sha256": digest(data)}
    command = ["python3", Path(__file__).relative_to(ROOT).as_posix(), recipe_path.relative_to(ROOT).as_posix()]
    if args.check:
        if output_path.read_bytes() != data or recipe.get("fingerprints") != fingerprints or recipe.get("command") != command:
            raise SystemExit("生成核对失败：产物、命令或输入指纹不匹配，请重新生成并验证")
        print(f"已核对：{recipe['output']}")
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(data)
    recipe["command"] = command
    recipe["fingerprints"] = fingerprints
    recipe_path.write_text(json.dumps(recipe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已生成：{recipe['output']}（{len(lines)}行）")


if __name__ == "__main__":
    main()
