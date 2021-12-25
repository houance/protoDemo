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


    def recvThread(self, dataQueue:Queue, cycleQueue:Queue):
        while True:
            if (self.rfile.readable):
                header = errorHandler.emptyCycleQueueErrorHeader(
                    lambda: cycleQueue.get_nowait()
                )


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

                    continue

                try:
                    request = cycleQueue.get_nowait()
                except Empty:
                    self.server.logger.warning('Empty CycleQueue', exc_info=True)
                    request = Request

                err = errorHandler.recvRequestError(
                    lambda: BinaryFramer.recvRequest(header, request, self.rfile),
                    self.server.logger
                )
                if err:
                    self.encounterError = True
                    return

                dataQueue.put_nowait(header)
                dataQueue.put_nowait(request)
            else:
                time.sleep(0.001)


    def threadedHandle(self):
        dataQueue = Queue(0)
        predictor = YuNet(self.server.path)

        recvThread = Thread(target=self.recvThread, args=(dataQueue,), daemon=True)
        recvThread.start()

        while not self.encounterError:
            if dataQueue.qsize() != 0:
                try:
                    header = dataQueue.get_nowait()
                except Empty:
                    continue

                while not self.encounterError:
                    try:
                        request = dataQueue.get_nowait()
                    except Empty:
                        continue
                    
                    if (request.encodeJpg is None):
                        continue
                    
                    frame = NetTransfer.decodeFrame(request.encodeJpg)
                    result = predictor.predict(frame)

                    response = Response()
                    response.faces = result

                    err = errorHandler.sendResponseError(
                        lambda: BinaryFramer.sendResponse(header, response, self.wfile),
                        self.server.logger
                    )
                    if err:return
                    else: break
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