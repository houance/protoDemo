from io import BytesIO
from socket import socket
from yuNet import Header, Request, Response


class BinaryFramer:
    @staticmethod
    def recvHeader(header:Header, socketReader:BytesIO):
        data = socketReader.read(10)

        return header.ParseFromString(data)

    @staticmethod
    def recvResponse(header:Header, response:Response, socketReader:BytesIO):
        data = socketReader.read(int(header.length))

        return response.ParseFromString(data)

    @staticmethod
    def sendRequest(header:Header, request:Request, socketWriter:socket):
        data = request.SerializeToString()

        header.length = len(data)
        if header.length <= 0 or header.length > 4294967295:
            raise ValueError("Request's Length Must Greater Than Zero and Smaller than 2^32 -1")

        socketWriter.sendall(header.SerializeToString() + data)