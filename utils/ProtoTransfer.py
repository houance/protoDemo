from NetTransfer import NetTransfer
from yuNet import Header, Request, Response

class ProtoTransfer:
    @staticmethod
    def serialize(object):
        return object.SerializeToString()

    @staticmethod
    def deserialize(object):
        return 