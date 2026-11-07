from __future__ import annotations

from _bootstrap_tfwr_orchestrator import add_orchestrator_src_to_path


add_orchestrator_src_to_path()


from tfwr_orchestrator.leaderboard_sync import main


if __name__ == "__main__":
    raise SystemExit(main())
