import os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ok')
    def log_message(self, *a): pass

port = int(os.getenv('PORT', 8080))
print(f'STARTING on {port}', flush=True)
HTTPServer(('0.0.0.0', port), H).serve_forever()
