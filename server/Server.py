from io import BufferedIOBase
import socket
from utils.NetTransfer import NetTransfer
from server.BianryFramer import Wrapper
from cv.YuNet import YuNet
from yuNet import Header, Request, Response
import socketserver


class Server(socketserver.StreamRequestHandler):
    def setup(self):
        self.connection = self.request
        if self.timeout is not None:
            self.connection.settimeout(self.timeout)
        if self.disable_nagle_algorithm:
            self.connection.setsockopt(socket.IPPROTO_TCP,
                                    socket.TCP_NODELAY, True)
        self.rfile = self.connection.makefile('rb', self.rbufsize)
        if self.wbufsize == 0:
            self.wfile = _SocketWriter(self.connection)
        else:
            self.wfile = self.connection.makefile('wb', self.wbufsize)

        self.predictor = YuNet()
        self.header = Header()
        self.request = Request()
        self.response = Response()
    
    def handle(self) -> None:
        while True:
            Wrapper.recvHeader(self.header, self.rfile)
            Wrapper.recvRequest(self.header, self.request, self.rfile)

            frame = NetTransfer.decodeFrame(self.request.encodeJpg)
            result = self.predictor.predict(frame, False)

            if result is not None:
                self.response.faces = result

            Wrapper.sendResponse(self.header, self.response, self.wfile)
        
class _SocketWriter(BufferedIOBase):
    """Simple writable BufferedIOBase implementation for a socket

    Does not hold data in a buffer, avoiding any need to call flush()."""

    def __init__(self, sock):
        self._sock = sock

    def writable(self):
        return True

    def write(self, b):
        self._sock.sendall(b)
        with memoryview(b) as view:
            return view.nbytes

    def fileno(self):
        return self._sock.fileno()
        