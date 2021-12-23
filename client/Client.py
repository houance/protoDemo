import socket
from utils.NetTransfer import NetTransfer
from client.BinaryFramer import BinaryFramer
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
        frame = NetTransfer.resize(frame)
        jpg = NetTransfer.encodeFrame(frame)

        self.request.encodeJpg = jpg

        BinaryFramer.sendRequest(self.header, self.request, self.writer)

        BinaryFramer.recvHeader(self.header, self.reader)
        if self.header.streamID == 0:
            print("server side encounter error")
            return
        elif self.header.length == 0:
            print("wrong frame data formate")
            return

        BinaryFramer.recvResponse(self.header, self.response, self.reader)

        return NetTransfer.decodeYuNetPredictServerResult(self.response.faces)