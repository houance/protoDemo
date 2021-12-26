import logging
from queue import Empty, Queue
from types import LambdaType


class DynamicQueue:
    def __init__(self, maxSizeThreshold:int, funcNew:LambdaType, logger:logging.Logger) -> None:
        self.queue = Queue(0)
        self.maxSizeThreshold = maxSizeThreshold
        self.spareSize = int(maxSizeThreshold*0.8)
        self.func = funcNew
        self.initQueue()
        self.logger = logger

    def get(self):
        try:
            item = self.queue.get_nowait()
        except Empty:
            item = self.func()
            self.maxSizeThreshold = int(self.maxSizeThreshold * 0.5) + 1
            self.spareSize = int(self.maxSizeThreshold*0.8)
            self.logger.warning('Empty CycleQueue, Expand Size to %d ', self.maxSizeThreshold,  exc_info=True)
        finally:
            return item

    def put(self, item):
        if self.queue.qsize() >= self.spareSize:
            return
        else:
            self.queue.put_nowait(item)

    def initQueue(self):
        for _ in range(0, self.maxSizeThreshold):
            self.queue.put_nowait(self.func())
