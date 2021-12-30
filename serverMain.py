from server.Server import Server, Handler
from argparse import ArgumentParser
import logging


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
    consoleHandler.setLevel(logging.ERROR)
    consoleHandler.setFormatter(formatter)

    logToFileHandler = logging.FileHandler('app.log')
    logToFileHandler.setLevel(logging.INFO)
    logToFileHandler.setFormatter(formatter)

    logger.addHandler(consoleHandler)
    logger.addHandler(logToFileHandler)

    with Server((args.address, args.port), Handler, args.path, logger, True) as server:
        server.serve_forever()
