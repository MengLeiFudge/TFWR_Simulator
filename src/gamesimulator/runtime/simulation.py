from __future__ import annotations

import heapq
from typing import Any
import random

from ..common.duration import Duration
from ..common.helper import just_sha256_it
from ..common.runtime_types import TimerRecord


class Simulation:
    BASE_OP_DURATION = 0.0025

    def __init__(self, seed: int = -1):
        self.execution = None
        self.main_sim = None
        self.has_error = False
        self._timers: list[tuple[int, TimerRecord]] = []
        self._timer_seq = 0
        self.step_by_step_mode = False
        if seed >= 0:
            self.random = random.Random(seed)
        else:
            self.random = random.Random()
        self.random_various = random.Random(just_sha256_it(self.random))
        self.random_maze = random.Random(just_sha256_it(self.random))
        self.random_snake = random.Random(just_sha256_it(self.random))
        self.random_cactus = random.Random(just_sha256_it(self.random))
        self.random_sunflower = random.Random(just_sha256_it(self.random))
        self.random_pumpkin = random.Random(just_sha256_it(self.random))
        self.random_poly = random.Random(just_sha256_it(self.random))
        self.random_random = random.Random(just_sha256_it(self.random))
        self.speed_factor = 1.0
        self.op_duration = Duration.from_seconds(self.BASE_OP_DURATION)
        self.current_time = Duration(0)
        self.paused = False
        self.logs: list[str] = []
        self.log_sink = None
        self.capture_logs = True
        self._farm = None

    @property
    def farm(self):
        return self._farm

    @farm.setter
    def farm(self, value) -> None:
        self._farm = value
        if value is not None:
            value.sim = self
            self.change_execution_speed(value.max_speed_factor())

    def is_executing(self) -> bool:
        return self.execution is not None

    def start_program_execution(self, execution: Any) -> None:
        if self.is_executing():
            raise RuntimeError("Tried to start a simulation twice")
        self.execution = execution
        self.next_execution_step()

    def stop_program_execution(self) -> None:
        self.execution = None
        self.paused = False
        self.has_error = False

    def error(self) -> None:
        self.has_error = True
        self.paused = True

    def start_timer(self, func, time: Duration) -> TimerRecord:
        timer = TimerRecord(self.current_time + time, func)
        self._timer_seq += 1
        heapq.heappush(self._timers, (timer.finish_time.nanoseconds, self._timer_seq, timer))
        return timer

    def pop_due_timer(self, goal_time: Duration) -> TimerRecord | None:
        while self._timers and self._timers[0][2].stopped and self.current_time < goal_time:
            heapq.heappop(self._timers)
        if not self._timers:
            return None
        finish_ns, _, timer = self._timers[0]
        if finish_ns > goal_time.nanoseconds:
            return None
        heapq.heappop(self._timers)
        self.current_time = timer.finish_time
        return timer

    def change_execution_speed(self, speed_factor: float) -> None:
        self.op_duration = Duration(int((2_500_000 + speed_factor - 1) // speed_factor) if isinstance(speed_factor, int) else int(__import__("math").ceil(2_500_000.0 / speed_factor)))
        self.speed_factor = speed_factor

    def next_execution_step(self) -> None:
        if self.execution is not None and not self.execution.is_performing_a_step:
            self.paused = False
            self.execution.next_execution_time = self.current_time

    def run_next_step(self, goal_time: Duration, stop_on_finished: bool = False) -> None:
        if self.paused or (stop_on_finished and not self.is_executing()):
            return
        if self.is_executing() and self.has_error:
            self.stop_program_execution()
            return
        while self._timers and self.current_time < goal_time and self._timers[0][2].stopped:
            heapq.heappop(self._timers)
        next_timer_finish = self._timers[0][2].finish_time if self._timers else None
        execution_ready = self.is_executing() and self.execution.next_execution_time <= goal_time
        timer_ready = next_timer_finish is not None and next_timer_finish <= goal_time
        if not execution_ready and not timer_ready:
            self.current_time = goal_time
            return
        if timer_ready and (not self.is_executing() or self.execution.next_execution_time >= next_timer_finish):
            self.current_time = next_timer_finish
            _, _, timer = heapq.heappop(self._timers)
            timer.func()
            return
        self.current_time = self.execution.next_execution_time
        priority2 = next_timer_finish if next_timer_finish is not None else goal_time
        priority2 = Duration(priority2.nanoseconds - 1) if priority2.nanoseconds > 0 else priority2
        target_run_time = Duration.min(priority2, goal_time) - self.current_time
        self.execution.execute(target_run_time)

    def add_ops_to_current_time(self, ops: float) -> None:
        delta = self.op_duration * ops
        self.current_time = self.current_time + delta
        if self.farm is not None:
            self.farm.passive_update(delta.seconds, self.random_various)

    def get_action_time(self, ops: float) -> Duration:
        return self.op_duration * ops

    def log(self, message: str) -> None:
        if self.capture_logs:
            self.logs.append(message)
        if self.log_sink is not None:
            self.log_sink(message)
