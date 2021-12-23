from typing import Callable
from utils.NetTransfer import NetTransfer
from server.BinaryFramer import BinaryFramer
from cv.YuNet import YuNet
from yuNet import Header, Request, Response
import socketserver


class Server(socketserver.TCPServer):
    def __init__(self, server_address: tuple, RequestHandlerClass: Callable[..., socketserver.BaseRequestHandler],  path:str, bind_and_activate: bool = True,) -> None:
        super().__init__(server_address, RequestHandlerClass, bind_and_activate=bind_and_activate)
        self.path = path

class Handler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        predictor = YuNet(self.server.path)
        header = Header()
        request = Request()
        response = Response()
        while True:
            try:
                BinaryFramer.recvHeader(header, self.rfile)
            except:
                BinaryFramer.sendErrorHeader(header, self.wfile)
                continue

            try:
                BinaryFramer.recvRequest(header, request, self.rfile)
            except:
                BinaryFramer.sendErrorHeader(header, self.wfile, False)
                continue

            frame = NetTransfer.decodeFrame(request.encodeJpg)
            result = predictor.predict(frame, False)

            response.faces = result

            BinaryFramer.sendResponse(header, response, self.wfile)
