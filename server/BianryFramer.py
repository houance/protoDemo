from yuNet import Header, Request, Response
from io import BytesIO


class Wrapper:
    @staticmethod
    def recvHeader(header:Header, socketReader:BytesIO):
        data = socketReader.read(10)

        return header.ParseFromString(data)

    @staticmethod
    def recvRequest(header:Header, request:Request, socketReader:BytesIO):
        data = socketReader.read(int(header.length))

        return request.ParseFromString(data)

    @staticmethod
    def sendResponse(header:Header, response:Response, socketWriter:BytesIO):
        data = response.SerializeToString()

        header.length = len(data)

        socketWriter.write(header.SerializeToString() + data)
        # Wrapper.sendAll(header.SerializeToString() + data, socketWriter)

    @staticmethod
    def sendAll(data:bytes, socketWriter:BytesIO):
        data = memoryview(data)

        remain = socketWriter.write(data)
        while remain:
            data = data[remain:]
            remain = socketWriter(data)

        socketWriter.flush()