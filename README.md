# TFWR_Simulator

独立的 `gamesimulator` Python 仓库。真实 `Save0` 仍保留在游戏目录；仓库只保留 `lb_*.py` 的参考副本，不把整个存档当成源码管理。

## 目录结构

```text
leaderboard/                     # 指向真实 Save0 的本地链接目录
references/
├── DecompiledSource/            # 反编译源码参考
└── leaderboard_scripts/         # 仓库内参考的 lb_*.py
src/
└── gamesimulator/               # 真实 Python 包
```

## 本地配置

1. 复制 `.env.example` 为 `.env`
2. 在 `.env` 中设置：

```env
TFWR_SAVE_ROOT=C:\Users\MLJ\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced\Saves\Save0
```

`.env` 不进 git；如果你已经在 shell 里设置了 `TFWR_SAVE_ROOT`，代码会优先使用环境变量。

如果你修改了 `.env` 中的 `TFWR_SAVE_ROOT`，请显式重建 `leaderboard` 链接：

```bash
python tools/refresh_leaderboard_link.py
```

## 同步打榜脚本

仓库只跟踪 `references/leaderboard_scripts/` 里的 `lb_*.py`。  
`leaderboard/` 与参考目录之间的同步必须显式触发：

```bash
py tools/sync_leaderboard_scripts.py save2cur
py tools/sync_leaderboard_scripts.py cur2save
py tools/sync_leaderboard_scripts.py
```

- `save2cur`：`leaderboard/ -> references/leaderboard_scripts/`
- `cur2save`：`references/leaderboard_scripts/ -> leaderboard/`
- 不带参数时会提示输入 `1` 或 `2`
- 无论哪个方向，都只复制 `lb_*.py`

## 运行

仓库根目录直接运行：

```bash
py runner.py simulate.py
py runner.py test.py
py runner.py lb_wood_single.py 1 10000
```

也可以直接走包入口：

```bash
PYTHONPATH=src python -m gamesimulator.runner simulate.py
```

CLI 参数格式：

```text
runner.py <target> [seed] [speedup] [save_root]
```

- `target`：`simulate.py` / `test.py` / `lb_*.py`
- `seed`：默认 `1`
- `speedup`：保留兼容位，默认 `10000`
- `save_root`：可选；不传时从 `.env` / `TFWR_SAVE_ROOT` 读取

## 测试

```bash
python -m unittest tests.test_gamesimulator
python -m unittest tests.test_tooling
```

测试里依赖真实 `Save0/__builtins__.py` 的部分也会读取 `.env` / `TFWR_SAVE_ROOT`。

默认 unlock 快照不再使用文本 dump 文件，而是内置在 `src/gamesimulator/unlock_snapshot.py`。
