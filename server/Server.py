from typing import Callable
from utils.NetTransfer import NetTransfer
from server.BianryFramer import Wrapper
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
            Wrapper.recvHeader(header, self.rfile)
            Wrapper.recvRequest(header, request, self.rfile)

            frame = NetTransfer.decodeFrame(request.encodeJpg)
            result = predictor.predict(frame, False)

            if result is not None:
                response.faces = result

            Wrapper.sendResponse(header, response, self.wfile)
