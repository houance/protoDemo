from queue import Empty
from yuNet import DecodeError, Header, Request, Response
import logging


class YuNetErrorHandle:
    @staticmethod
    def recvResponseError(func, logger:logging.Logger) -> bool:
        try:
            func()
        except (DecodeError, OSError) as e:
            logger.error('Error Happen While Receive Header', exc_info=True)
            return True
        return False
    
    @staticmethod
    def recvRequestError(func, logger:logging.Logger) -> bool:
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
    def sendResponseError(func, logger:logging.Logger) -> bool:
        try:
            func()
        except OSError:
            logger.error('Error Happen While Send Response', exc_info=True)
            return True
        return False

    @staticmethod
    def sendResponseError(func, logger:logging.Logger) -> bool:
        try:
            func()
        except OSError:
            logger.error('Error Happen While Send Response', exc_info=True)
            return True
        return False

    @staticmethod
    def emptyCycleQueueErrorHeader(func, logger:logging.Logger) -> Header:
        try:
            header = func()
        except Empty:
            logger.warning('Empty CycleQueue', exc_info=True)
            header = Header()
        finally:
            return header

    @staticmethod
    def emptyCycleQueueErrorRequest(func, logger:logging.Logger) -> Request:
        try:
            request = func()
        except Empty:
            logger.warning('Empty CycleQueue', exc_info=True)
            request = Request()
        finally:
            return request

    @staticmethod
    def emptyCycleQueueErrorResponse(func, logger:logging.Logger) -> Response:
        try:
            response = func()
        except Empty:
            logger.warning('Empty CycleQueue', exc_info=True)
            response = Response()
        finally:
            return response