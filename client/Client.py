import socket
from utils.NetTransfer import NetTransfer
from client.BinaryFramer import Wrapper
from yuNet import Header, Request, Response


class Client:
    def __init__(self, address:str, port:int, streamID=1) -> None:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((address, port))
        self.reader = client.makefile('rb')
        self.writer = client.makefile('wb')

        self.header = Header()
        self.header.streamID = streamID

        self.request = Request()
        self.response = Response()
        
    def send(self, frame):
        jpg = NetTransfer.encodeFrame(frame)

        self.request.encodeJpg = jpg

        Wrapper.sendRequest(self.header, self.request, self.writer)

        Wrapper.recvResponse(self.header, self.response, self.reader)

        return NetTransfer.decodeYuNetPredictServerResult(self.response.faces)