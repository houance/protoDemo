from typing import BinaryIO
from yuNet import Header, Request, Response


class BinaryFramer:
    @staticmethod
    def recvHeader(header:Header, socketReader:BinaryIO):
        data = socketReader.read(10)
        if len(data) == 0:
            raise ValueError('Closed Socket File')

        return header.ParseFromString(data)

    @staticmethod
    def recvRequest(header:Header, request:Request, socketReader:BinaryIO):
        length = int(header.length)

        data = socketReader.read(length)
        if len(data) != length:
            raise ValueError('Closed Socket File')

        return request.ParseFromString(data)

    @staticmethod
    def sendResponse(header:Header, response:Response, socketWriter:BinaryIO):
        data = response.SerializeToString()

        header.length = len(data)
        if header.length <= 0 or header.length > 4294967295:
            raise ValueError("Response's Length Must Greater Than Zero and Smaller than 2^32 -1")
        socketWriter.write(header.SerializeToString() + data)

    @staticmethod
    def sendHeader(header:Header, socketWriter:BinaryIO):
        socketWriter.write(header.SerializeToString())
