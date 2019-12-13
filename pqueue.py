import heapq
from typing import Callable, Any, Tuple, List


class SortingQueue:
    _key: Callable[[Any], Any]
    _data: List[Tuple[Any, Any]]

    def __init__(self, initial: List[Any] = None, key=lambda x: x):
        self._key = key
        if initial:
            self._data = [(key(item), item) for item in initial]
            heapq.heapify(self._data)
        else:
            self._data = []

    def push(self, item):
        heapq.heappush(self._data, (self._key(item), item))

    def pop(self):
        return heapq.heappop(self._data)[1]
