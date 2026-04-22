from __future__ import annotations

from _bootstrap_tfwr_orchestrator import add_orchestrator_src_to_path


add_orchestrator_src_to_path()


from tfwr_orchestrator.config import refresh_leaderboard_link


def main() -> int:
    link_path, target = refresh_leaderboard_link()
    print(f"leaderboard_link {link_path} -> {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
