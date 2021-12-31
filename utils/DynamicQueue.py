import logging
from types import LambdaType
from collections import deque


class CycleQueue:
    def __init__(self, maxSizeThreshold:int, funcNew:LambdaType, logger:logging.Logger) -> None:
        self.newQueue = deque()
        self.manipulatedQueue = deque()
        self.maxSizeThreshold = maxSizeThreshold
        self.spareSize = int(maxSizeThreshold*0.8)
        self.func = funcNew
        self.initQueue()
        self.logger = logger

    
    def getManipulatedItem(self):
        while not len(self.manipulatedQueue):
            continue
        return self.manipulatedQueue.popleft()

    def getNewItem(self):
        try:
            item = self.newQueue.popleft()
        except IndexError:
            item = self.func()
            self.maxSizeThreshold = int(self.maxSizeThreshold * 1.5) + 1
            self.spareSize = int(self.maxSizeThreshold*0.8)
            self.logger.warning('Empty CycleQueue, Expand Size to %d ', self.maxSizeThreshold,  exc_info=True)
        finally:
            return item

    def putIntoNewQueue(self, item):
        if len(self.newQueue) >= self.spareSize:
            return
        else:
            self.newQueue.append(item)

    def putIntoManipulatedQueue(self, item):
        self.manipulatedQueue.append(item)

    def initQueue(self):
        for _ in range(0, self.maxSizeThreshold):
            item = self.func()
            self.newQueue.append(item)
