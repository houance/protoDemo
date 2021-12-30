from types import LambdaType
from yuNet import DecodeError
import logging


class YuNetErrorHandle:
    @staticmethod
    def recvHeaderError(func:LambdaType, logger:logging.Logger) -> bool:
        try:
            func()
        except (DecodeError, OSError) as e:
            logger.error('Error Happen While Receive Header', exc_info=True)
            return True
        return False

    @staticmethod
    def recvRequestError(func:LambdaType, logger:logging.Logger) -> bool:
        try:
            func()
        except DecodeError as e:
            logger.error('Error Happen While Decode Request', exc_info=True)
            return False
        except OSError as e:
            logger.error('Error Happen While Receive Request', exc_info=True)
            return True
        return False

    @staticmethod
    def sendResponseError(func:LambdaType, logger:logging.Logger) -> bool:
        try:
            func()
        except OSError:
            logger.error('Error Happen While Send Response', exc_info=True)
            return True
        return False
