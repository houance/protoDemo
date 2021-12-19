from io import BytesIO
from yuNet import Header, Request, Response


class Wrapper:
    @staticmethod
    def recvHeader(header:Header, socketReader:BytesIO):
        data = socketReader.read(10)

        return header.ParseFromString(data)

    @staticmethod
    def recvResponse(header:Header, response:Response, socketReader:BytesIO):
        Wrapper.recvHeader(header, socketReader)

        data = socketReader.read(int(header.length))

        return response.ParseFromString(data)

    @staticmethod
    def sendRequest(header:Header, request:Request, socketWriter:BytesIO):
        data = request.SerializeToString()

        header.length = len(data)

        socketWriter.write(header.SerializeToString() + data)