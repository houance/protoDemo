from types import LambdaType
from yuNet import DecodeError
import logging


class YuNetErrorHandle:
    @staticmethod
    def recvHeaderError(func:LambdaType, logger:logging.Logger) -> bool:
        try:
            func()
        except DecodeError:
            logger.error('Error Happen While Decode Header', exc_info=True)
            return True
        except (OSError, ValueError):
            logger.warning('Error Happen While Receive Header, Mainly Lost Connection', 
            exc_info=True)
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
            logger.warning('Error Happen While Receive Header, Mainly Lost Connection',
             exc_info=True)
            return True
        else:
            return False

    @staticmethod
    def sendResponseError(func:LambdaType, logger:logging.Logger) -> bool:
        try:
            func()
        except (OSError, ValueError):
            logger.warning('Error Happen While Receive Header, Mainly Lost Connection', 
            exc_info=True)
            return True
        else:
            return False
