import time
from types import LambdaType


class Common:
    @staticmethod
    def timeIt(func:LambdaType) -> float:
        start = time.time()
        func()
        return time.time() - start

    @staticmethod
    def timeItString(func:LambdaType) -> str:
        start = time.time()
        func()
        return str(time.time() - start)