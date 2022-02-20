from server.Server import Server, Handler
from argparse import ArgumentParser
import logging
from utils.ConsulTool import ConsulTool


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument('--address',
                        type=str,
                        help='start address',
                        required=True)
    parser.add_argument('--port',
                        type=int,
                        help='start port',
                        required=True)
    parser.add_argument('--path',
                        type=str,
                        help='onnx path',
                        required=False,
                        default='./model/YuFaceDetectNet.onnx')
    parser.add_argument('--threaded',
                    type=bool,
                    help='threaded or not',
                    required=False,
                    default=True)
    args = parser.parse_args()

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")

    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.DEBUG)
    consoleHandler.setFormatter(formatter)

    logToFileHandler = logging.FileHandler('app.log')
    logToFileHandler.setLevel(logging.WARNING)
    logToFileHandler.setFormatter(formatter)

    logger.addHandler(consoleHandler)
    logger.addHandler(logToFileHandler)
    c = ConsulTool('172.17.129.202', 8500)

    with Server((args.address, args.port), Handler, args.path, logger, True) as server:
        logger.info("Start Server")
        c.registerServerService('yuNetServer', '172.30.58.167', args.port)
        server.serve_forever()
