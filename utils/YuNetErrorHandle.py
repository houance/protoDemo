from types import LambdaType
from yuNet import DecodeError
import logging


class YuNetErrorHandle:
    @staticmethod
    def recvHeaderError(func:LambdaType, logger:logging.Logger) -> bool:
        try:
            func()
        except:
            logger.error('Error Happen While Receive Header', exc_info=True)
            return True
        else: 
            return False

    @staticmethod
    def recvRequestError(func:LambdaType, logger:logging.Logger) -> bool:
        try:
            func()
        except DecodeError:
            logger.error('Error Happen While Decode Request', exc_info=True)
            return False
        except (OSError, ValueError):
            logger.error('Error Happen While Receive Request', exc_info=True)
            return True
        else:
            return False

    @staticmethod
    def sendResponseError(func:LambdaType, logger:logging.Logger) -> bool:
        try:
            func()
        except (OSError, ValueError):
            logger.error('Error Happen While Send Response', exc_info=True)
            return True
        else:
            return False
