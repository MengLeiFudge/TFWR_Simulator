"""纳秒定时事件；复现原版四叉优先队列的同刻事件顺序。"""

from dataclasses import dataclass


@dataclass
class Timer:
    """取消事件留在堆中，直到成为堆顶；提前删除会改变同刻事件顺序。"""
    at: int
    callback: object
    stopped: bool = False


class Timers:
    """只以时间比较优先级，不附加FIFO序号；与游戏Utils四叉堆一致。"""

    def __init__(self):
        self.heap = []

    def start(self, at, callback):
        """在绝对游戏纳秒时刻调用callback，返回可取消句柄。"""
        timer = Timer(int(at), callback)
        index = len(self.heap)
        self.heap.append(timer)
        while index:
            parent = (index - 1) >> 2
            if timer.at >= self.heap[parent].at:
                break
            self.heap[index] = self.heap[parent]
            index = parent
        self.heap[index] = timer
        return timer

    def pop(self):
        """移除堆顶；相同优先级保留首个子节点，尾节点相等时停止下沉。"""
        first = self.heap[0]
        tail = self.heap.pop()
        if self.heap:
            index = 0
            while (child := (index << 2) + 1) < len(self.heap):
                child = min(range(child, min(child + 4, len(self.heap))), key=lambda i: self.heap[i].at)
                if tail.at <= self.heap[child].at:
                    break
                self.heap[index] = self.heap[child]
                index = child
            self.heap[index] = tail
        return first

    def next_time(self):
        """跳过堆顶取消项；空队列返回无穷大。"""
        while self.heap and self.heap[0].stopped:
            self.pop()
        return self.heap[0].at if self.heap else float('inf')
