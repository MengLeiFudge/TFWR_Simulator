"""通过游戏随附Steam SDK只读排行榜，复用公开缓存的数据校验与账号边界。"""
from __future__ import annotations

import ctypes as c
import os
import sys
import time

from .config import resolve_steam_api_path
from .leaderboard_cache import (
    APP_ID, BOARD_IDS, PAGE_SIZE, AccountSnapshot, BoardSnapshot, RankEntry,
    account_identity, board_url, utc_now, validate_snapshot,
)


# 基础多机榜的Steam内部名带_multi，游戏枚举和脚本名保持原名称。
MULTI_BOARDS = {
    "lb_cactus", "lb_carrots", "lb_dinosaur", "lb_fastest_reset", "lb_hay",
    "lb_maze", "lb_pumpkins", "lb_sunflowers", "lb_wood",
}


class _Found(c.Structure):
    _pack_ = 8
    _fields_ = [("handle", c.c_uint64), ("found", c.c_uint8)]


class _Downloaded(c.Structure):
    _pack_ = 8
    _fields_ = [("board", c.c_uint64), ("entries", c.c_uint64), ("count", c.c_int)]


class _Entry(c.Structure):
    _pack_ = 8
    _fields_ = [("user", c.c_uint64), ("rank", c.c_int), ("score", c.c_int),
                ("details", c.c_int), ("ugc", c.c_uint64)]


class SteamLeaderboardReader:
    """一个上下文持有Steam客户端，调用方串行抓取，退出时释放并恢复进程环境。"""

    def __init__(self, owner: str | None, timeout: float):
        if sys.platform != "win32" or c.sizeof(c.c_void_p) != 8:
            raise RuntimeError("--steam需要64位Windows Python；WSL中请使用py.exe。")
        if owner is None:
            raise RuntimeError("--steam需要安装清单LastOwner，以核对当前Steam账号。")
        self.owner = owner
        self.timeout = timeout
        self.dll = c.CDLL(str(resolve_steam_api_path()))
        self.initialized = False
        self.environment: dict[str, str | None] = {}

    def _bind(self, name, result, args):
        fn = getattr(self.dll, "SteamAPI_" + name)
        fn.restype = result
        fn.argtypes = args
        return fn

    def _interface(self, name, versions):
        for version in versions:
            try:
                fn = self._bind(name + "_v" + str(version).zfill(3), c.c_void_p, [])
            except AttributeError:
                continue
            value = fn()
            if value:
                return value
        raise RuntimeError("Steam客户端接口不可用：" + name)

    def __enter__(self):
        self.environment = {key: os.environ.get(key) for key in ("SteamAppId", "SteamGameId")}
        for key in self.environment:
            os.environ[key] = str(APP_ID)
        try:
            if not self._bind("Init", c.c_bool, [])():
                raise RuntimeError("Steam客户端未就绪；请先登录Steam后重试。")
            self.initialized = True
            self.stats = self._interface("SteamUserStats", [13, 12, 11])
            self.utils = self._interface("SteamUtils", [10, 9])
            user = self._interface("SteamUser", [23, 22, 21])
            self.account = self._bind("ISteamUser_GetSteamID", c.c_uint64, [c.c_void_p])(user)
            if str(self.account) != self.owner:
                raise RuntimeError("当前Steam客户端与安装清单账号不一致，停止更新账号记录。")
            self.find = self._bind("ISteamUserStats_FindLeaderboard", c.c_uint64, [c.c_void_p, c.c_char_p])
            self.download = self._bind("ISteamUserStats_DownloadLeaderboardEntries", c.c_uint64,
                                       [c.c_void_p, c.c_uint64, c.c_int, c.c_int, c.c_int])
            self.own = self._bind("ISteamUserStats_DownloadLeaderboardEntriesForUsers", c.c_uint64,
                                  [c.c_void_p, c.c_uint64, c.POINTER(c.c_uint64), c.c_int])
            self.entry = self._bind("ISteamUserStats_GetDownloadedLeaderboardEntry", c.c_bool,
                                    [c.c_void_p, c.c_uint64, c.c_int, c.POINTER(_Entry), c.POINTER(c.c_int), c.c_int])
            self.completed = self._bind("ISteamUtils_IsAPICallCompleted", c.c_bool,
                                        [c.c_void_p, c.c_uint64, c.POINTER(c.c_bool)])
            self.result = self._bind("ISteamUtils_GetAPICallResult", c.c_bool,
                                     [c.c_void_p, c.c_uint64, c.c_void_p, c.c_int, c.c_int, c.POINTER(c.c_bool)])
            self.count = self._bind("ISteamUserStats_GetLeaderboardEntryCount", c.c_int, [c.c_void_p, c.c_uint64])
            return self
        except BaseException:
            self.__exit__()
            raise

    def __exit__(self, *_):
        try:
            if self.initialized:
                self._bind("Shutdown", None, [])()
                self.initialized = False
        finally:
            for key, value in self.environment.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def _wait(self, call, struct, callback):
        if not call:
            raise RuntimeError("Steam排行榜请求未创建。")
        deadline = time.monotonic() + self.timeout
        failed = c.c_bool()
        while not self.completed(self.utils, call, c.byref(failed)):
            if time.monotonic() >= deadline:
                raise TimeoutError("Steam排行榜查询超时。")
            time.sleep(0.05)
        value = struct()
        if (failed.value or not self.result(self.utils, call, c.byref(value), c.sizeof(value),
                                            callback, c.byref(failed)) or failed.value):
            raise RuntimeError("Steam排行榜回调失败。")
        return value

    def _rows(self, value, maximum: int, own: bool = False) -> tuple[RankEntry, ...]:
        if not 0 <= value.count <= maximum:
            raise ValueError("Steam返回条目数越界。")
        rows = []
        for index in range(value.count):
            item = _Entry()
            if not self.entry(self.stats, value.entries, index, c.byref(item), None, 0):
                raise RuntimeError("Steam排行榜条目读取失败。")
            if own and item.user != self.account:
                raise ValueError("Steam账号响应不属于当前账号。")
            rows.append(RankEntry(item.rank, item.score))
        return tuple(rows)

    def fetch(self, script: str, limit: int) -> BoardSnapshot:
        name = script.removeprefix("lb_") + ("_multi" if script in MULTI_BOARDS else "")
        found = self._wait(self.find(self.stats, name.encode("ascii")), _Found, 1104)
        if not found.found or found.handle != BOARD_IDS[script]:
            raise ValueError(f"{script}: Steam内部名称与公开榜单ID不一致。")
        # 首次下载刷新客户端的条目数；Find刚完成时该缓存可能尚未就绪。
        value = self._wait(self.download(self.stats, found.handle, 0, 1, min(limit, PAGE_SIZE)), _Downloaded, 1105)
        total = self.count(self.stats, found.handle)
        if value.board != found.handle or value.count != min(limit, PAGE_SIZE, total):
            raise ValueError("Steam公开排行榜首页缺失或归属错误。")
        entries = list(self._rows(value, PAGE_SIZE))
        for start in range(PAGE_SIZE + 1, min(limit, total) + 1, PAGE_SIZE):
            end = min(start + PAGE_SIZE - 1, limit, total)
            value = self._wait(self.download(self.stats, found.handle, 0, start, end), _Downloaded, 1105)
            if value.board != found.handle or value.count != end - start + 1:
                raise ValueError("Steam公开排行榜响应缺页或归属错误。")
            entries.extend(self._rows(value, PAGE_SIZE))
        value = self._wait(self.own(self.stats, found.handle, (c.c_uint64 * 1)(self.account), 1), _Downloaded, 1105)
        if value.board != found.handle or total != self.count(self.stats, found.handle):
            raise ValueError("Steam账号响应归属错误或查询期间榜单人数变化。")
        own = self._rows(value, 1, own=True)
        date = utc_now()
        account = AccountSnapshot("not_listed", date, identity=account_identity(self.owner))
        if own:
            account = AccountSnapshot("listed", date, own[0].rank, own[0].time_ms, account_identity(self.owner))
        board = BoardSnapshot(script, board_url(script), date, total, tuple(entries), limit, account,
                              transport="steamworks")
        validate_snapshot(board)
        return board
