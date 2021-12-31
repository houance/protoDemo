import logging
from typing import Callable
from proto.YuNetMessageType import HeaderRequest as combine
from utils.NetTransfer import NetTransfer
from server.BinaryFramer import BinaryFramer
from cv.YuNet import YuNet
from yuNet import Header, Request, Response
import socketserver
import time
from threading import Thread, Event
from utils.YuNetErrorHandle import YuNetErrorHandle as errorHandler
from utils.DynamicQueue import CycleQueue


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
            self.encounterError = False
            self.threadedHandle()
        else:
            self.nonThreadedHandle()


    def recvThread(self, cycleQueue:CycleQueue, eventReceived:Event, eventError:Event):
        while True:
            if self.rfile.readable():
                item = cycleQueue.getNewItem()

                err = errorHandler.recvHeaderError(
                    lambda: BinaryFramer.recvHeader(item.header, self.rfile),
                    self.server.logger)
                if err:
                    eventError.set()
                    eventReceived.set()
                    return

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
                        return
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
                    return
                else:
                    cycleQueue.putIntoManipulatedQueue(item)
                    eventReceived.set()
            else:
                time.sleep(0.02)


    def threadedHandle(self):
        cycleQueue = CycleQueue(10, lambda:combine(Header(), Request()), self.server.logger)
        predictor = YuNet(self.server.path)
        response = Response()
        eventReceived = Event()
        eventError = Event()

        Thread(
            target=self.recvThread, 
            args=(cycleQueue, eventReceived, eventError), 
            daemon=True,
            name='Receive-Decoed-Thread').start()

        while eventReceived.wait():
            eventReceived.clear()
            if not eventError.is_set():
                item = cycleQueue.getManipulatedItem()

                frame = NetTransfer.decodeFrame(item.request.encodeJpg)
                result = predictor.predict(frame)
                response.faces = result

                err = errorHandler.sendResponseError(
                    lambda: BinaryFramer.sendResponse(item.header, response, self.wfile),
                    self.server.logger
                )
                if err:
                    return
                else:
                    cycleQueue.putIntoNewQueue(item)


    def nonThreadedHandle(self):
        predictor = YuNet(self.server.path)
        header = Header()
        request = Request()
        response = Response()
        while True:
            if self.rfile.readable():
                try:
                    BinaryFramer.recvHeader(header, self.rfile)
                except:
                    BinaryFramer.sendErrorHeader(header, self.wfile)
                    print('empty header')
                    return

                try:
                    BinaryFramer.recvRequest(header, request, self.rfile)
                except:
                    BinaryFramer.sendErrorHeader(header, self.wfile, False)
                    print("wrong request")
                    return

                frame = NetTransfer.decodeFrame(request.encodeJpg)
                result = predictor.predict(frame, False)

                response.faces = result

                BinaryFramer.sendResponse(header, response, self.wfile)
            else:
                time.sleep(0.01)