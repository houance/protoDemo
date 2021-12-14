from server.Server import Server
import socketserver


if __name__ == "__main__":
    with socketserver.TCPServer(('127.0.0.1', 9000), Server) as server:
        server.serve_forever()
