import os
import sys
import json
import signal
from http.server import HTTPServer, BaseHTTPRequestHandler
import config
from main import run_pipeline

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        elif self.path == '/run':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            try:
                success = run_pipeline()
                self.wfile.write(json.dumps({
                    "status": "success" if success else "failed",
                    "message": "Pipeline completed" if success else "Pipeline failed"
                }).encode())
            except Exception as e:
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": str(e)
                }).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

def run_server():
    port = int(os.getenv('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f'Health server running on port {port}')

    # If RAILWAY_CRON is set, run pipeline immediately
    if os.getenv('RAILWAY_CRON'):
        print('CRON trigger detected. Running pipeline...')
        run_pipeline()

    server.serve_forever()

if __name__ == '__main__':
    run_server()
