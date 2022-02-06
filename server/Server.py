import logging
import threading
import datetime
from typing import Callable
from proto.YuNetMessageType import HeaderRequest as combine
from utils.NetTransfer import NetTransfer
from server.BinaryFramer import BinaryFramer
from cv.YuNet import YuNet
from yuNet import Header, Request, Response
import socketserver
from threading import Thread, Event
from utils.YuNetErrorHandle import YuNetErrorHandle as errorHandler
from utils.DynamicQueue import CycleQueue

# Server Side total cost around ~40ms
# Socket Recv and Send, Protobuf serilize and deserilize cost below 1ms
# Opencv Compute ~35ms
class Server(socketserver.TCPServer):
    def __init__(
        self, 
        server_address: tuple, 
        RequestHandlerClass: Callable[..., socketserver.BaseRequestHandler], 
        path:str, 
        logger:logging.Logger, 
        threadedHandle: bool = True, 
        bind_and_activate: bool = True) -> None:
        super().__init__(server_address, RequestHandlerClass, bind_and_activate=bind_and_activate)
        self.path = path
        self.threaded = threadedHandle
        self.logger = logger

class Handler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        if self.server.threaded:
            self.threadedHandle()
        else:
            self.nonThreadedHandle()


    def computeThread(self, cycleQueue:CycleQueue, eventReceived:Event, eventError:Event):
        predictor = YuNet(self.server.path)
        response = Response()
        while eventReceived.wait() and not eventError.is_set():
            eventReceived.clear()
            item = cycleQueue.getManipulatedItem()

            frame = NetTransfer.decodeFrame(item.request.encodeJpg)
            result = predictor.predict(frame)
            response.faces = result

            err = errorHandler.sendResponseError(
                lambda: BinaryFramer.sendResponse(item.header, response, self.wfile),
                self.server.logger
            )
            if err:
                eventError.set()
                break
            else:
                cycleQueue.putIntoNewQueue(item)
                # self.server.logger.info(
                #     'Send to Go Time : {}'.format(datetime.datetime.now()))
        self.server.logger.warning(
            '{} exit'.format(threading.currentThread().getName()))

    def threadedHandle(self):
        cycleQueue = CycleQueue(
            10, 
            lambda:combine(Header(), Request()), 
            self.server.logger)

        eventReceived = Event()
        eventError = Event()
        Thread(
            target=self.computeThread, 
            args=(cycleQueue, eventReceived, eventError),
            name='Compute-Thread').start()

        while not eventError.is_set():
            item = cycleQueue.getNewItem()
            err = errorHandler.recvHeaderError(
                lambda: BinaryFramer.recvHeader(item.header, self.rfile),
                self.server.logger)
            if err:
                eventError.set()
                eventReceived.set()
                break

            # enum logic define in message
            # implement here to increae speed
            # becase python calling function is expensive
            if item.header.streamID == 0 and item.header.length == 1:

                err = errorHandler.sendHeaderError(
                    lambda: BinaryFramer.sendHeader(item.header, self.wfile),
                    self.server.logger
                )
                if err:
                    eventError.set()
                    eventReceived.set()
                    break
                else :
                    cycleQueue.putIntoNewQueue(item)
                    continue
            err = errorHandler.recvRequestError(
                lambda: BinaryFramer.recvRequest(item.header, item.request, self.rfile),
                self.server.logger
            )
            if err:
                eventError.set()
                eventReceived.set()
                break
            else:
                cycleQueue.putIntoManipulatedQueue(item)
                eventReceived.set()
                # self.server.logger.info(
                #     'Recv From GO Time : {}'.format(datetime.datetime.now()))
