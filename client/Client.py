import socket
from utils.NetTransfer import NetTransfer
from client.BinaryFramer import BinaryFramer
from yuNet import Header, Request, Response
import datetime


class Client:
    def __init__(self, address:str, port:int, streamID=1) -> None:
        self.header = Header()
        if streamID <= 0 or streamID >= 4294967295:
            raise ValueError("StreamID Must Greater Than Zero and Smaller than 2^32 - 1")
        self.header.streamID = streamID
        self.request = Request()
        self.response = Response()

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((address, port))
        client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        client.settimeout(None)
        self.reader = client.makefile('rb', -1)
        self.writer = client
        
    def send(self, frame):
        
        frame = NetTransfer.resize(frame)
        jpg = NetTransfer.encodeFrame(frame)

        self.request.encodeJpg = jpg

        BinaryFramer.sendRequest(self.header, self.request, self.writer)

        BinaryFramer.recvHeader(self.header, self.reader)

        BinaryFramer.recvResponse(self.header, self.response, self.reader)

        # print(datetime.datetime.now())

        return NetTransfer.decodeYuNetPredictServerResult(self.response.faces)

    def sendGolangBenchmark(self, frame):
        frame = NetTransfer.resize(frame)
        jpg = NetTransfer.encodeFrame(frame)

        self.request.encodeJpg = jpg

        BinaryFramer.sendRequest(self.header, self.request, self.writer)