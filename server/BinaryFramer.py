from typing import BinaryIO
from yuNet import Header, Request, Response


class BinaryFramer:
    @staticmethod
    def recvHeader(header:Header, socketReader:BinaryIO):
        data = socketReader.read(10)

        return header.ParseFromString(data)

    @staticmethod
    def recvRequest(header:Header, request:Request, socketReader:BinaryIO):
        data = socketReader.read(int(header.length))

        return request.ParseFromString(data)

    @staticmethod
    def sendResponse(header:Header, response:Response, socketWriter:BinaryIO):
        data = response.SerializeToString()

        header.length = len(data)

        socketWriter.write(header.SerializeToString() + data)

    @staticmethod
    def sendErrorHeader(header:Header, socketWriter:BinaryIO, setStreamID=True):
        if setStreamID:
            header.streamID = 0
        header.length = 0

        socketWriter.write(header.SerializeToString())
