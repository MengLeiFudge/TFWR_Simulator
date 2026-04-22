# tfwr_orchestrator

`tfwr_orchestrator` 是本仓库里负责真实游戏 oracle 工作流的 Python 子项目。

它负责三类事情：

1. 解析 `.env` / `TFWR_SAVE_ROOT` / `TFWR_GAME_ROOT`
2. 部署 leaderboard 脚本，并生成派生入口 `lb_start.py`
3. 通过 `state.json` 请求 Unity 模组执行脚本，并读取：
   - 游戏 `output.txt`
   - `BepInEx/LogOutput.log`

仓库根目录的 `tools/*.py` 只是薄包装器。真正逻辑都在：

- `src/tfwr_orchestrator/config.py`
- `src/tfwr_orchestrator/leaderboard_sync.py`
- `src/tfwr_orchestrator/real_game_runner.py`
- `src/tfwr_orchestrator/output_capture.py`

开发期测试：

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py' -v
```
