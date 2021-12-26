import logging
from typing import Callable
from proto.YuNetMessageType import YuNetMessageType as message
from utils.NetTransfer import NetTransfer
from server.BinaryFramer import BinaryFramer
from cv.YuNet import YuNet
from yuNet import Header, Request, Response
import socketserver
from queue import Empty, Queue
import time
from threading import Thread
from utils.YuNetErrorHandle import YuNetErrorHandle as errorHandler
from utils.DynamicQueue import DynamicQueue


class Server(socketserver.TCPServer):
    def __init__(self, server_address: tuple, RequestHandlerClass: Callable[..., socketserver.BaseRequestHandler],  path:str, logger:logging.Logger, threadedHandle: bool = True, bind_and_activate: bool = True,) -> None:
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


    def recvThread(self, headerQueue:Queue, requestQueue:Queue, headerCycleQueue:DynamicQueue, requestCycleQueue:DynamicQueue):
        while True:
            if (self.rfile.readable):

                header = headerCycleQueue.get()

                err = errorHandler.recvHeaderError(
                    lambda: BinaryFramer.recvHeader(header, self.rfile),
                    self.server.logger)
                if err:
                    self.encounterError = True
                    return

                if message.isPingHeader(header):
                    message.ping(header)

                    err = errorHandler.sendHeaderError(
                        lambda: BinaryFramer.sendHeader(header, self.wfile),
                        self.server.logger
                    )
                    if err:
                        self.encounterError = True
                        return
                    headerCycleQueue.put(header)
                    continue

                request = requestCycleQueue.get()

                err = errorHandler.recvRequestError(
                    lambda: BinaryFramer.recvRequest(header, request, self.rfile),
                    self.server.logger
                )
                if err:
                    self.encounterError = True
                    return

                headerQueue.put_nowait(header)
                requestQueue.put_nowait(request)
            else:
                time.sleep(0.001)


    def threadedHandle(self):
        headerQueue = Queue(0)
        requestQueue = Queue(0)
        headerCycleQueue = DynamicQueue(20, lambda: Header(), self.server.logger)
        requestCycleQueue = DynamicQueue(20, lambda: Request(), self.server.logger)
        predictor = YuNet(self.server.path)
        response = Response()

        Thread(
            target=self.recvThread, 
            args=(headerQueue, requestQueue, headerCycleQueue, requestCycleQueue), 
            daemon=True,
            name='Receive-Decoed-Thread').start()

        while not self.encounterError:
            if headerQueue.qsize() != 0:
                try:
                    header = headerQueue.get_nowait()
                except Empty:
                    continue


                while not self.encounterError:
                    try:
                        request = requestQueue.get_nowait()
                    except Empty:
                        continue
                    
                    if (request.encodeJpg is None):
                        continue
                    
                    frame = NetTransfer.decodeFrame(request.encodeJpg)
                    result = predictor.predict(frame)
                    response.faces = result

                    err = errorHandler.sendResponseError(
                        lambda: BinaryFramer.sendResponse(header, response, self.wfile),
                        self.server.logger
                    )
                    if err:
                        return
                    else:
                        headerQueue.put(header)
                        requestQueue.put(request)

            else:
                time.sleep(0.001)        


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