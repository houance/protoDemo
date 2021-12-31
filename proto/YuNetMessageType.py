from yuNet import Header, Request


class HeaderRequest:
    def __init__(self, header:Header, request:Request) -> None:
        self.header = header
        self.request = request


class YuNetMessageType:
    @staticmethod
    def isPingHeader(header:Header):
        if header.streamID == 0 and header.length == 1:
            return True
        else:
            return False

    @staticmethod
    def ping(header:Header):
        header.streamID = 0
        header.length = 1

    @staticmethod
    def errorHeader(header:Header):
        header.streamID = 0
        header.length = 2