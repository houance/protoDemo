from http.server import BaseHTTPRequestHandler, HTTPServer

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.protocol_version = "HTTP/1.1"
        self.send_response_only(200)
        self.end_headers()
        return

def run():
    server = ('0.0.0.0', 12001)
    httpd = HTTPServer(server, RequestHandler)
    httpd.serve_forever()
run()