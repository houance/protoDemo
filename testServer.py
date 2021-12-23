from server.Server import Server, Handler
from argparse import ArgumentParser


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

    args = parser.parse_args()

    with Server((args.address, args.port), Handler, args.path) as server:
        server.serve_forever()
