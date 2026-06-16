import os
import sys
import json
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from main import run_pipeline
from search import search_new_videos

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
                print('Pipeline triggered via /run')
                success = run_pipeline()
                self.wfile.write(json.dumps({
                    "status": "success" if success else "failed",
                    "message": "Pipeline completed" if success else "Pipeline failed"
                }).encode())
            except Exception as e:
                tb = traceback.format_exc()
                print(f'Pipeline error: {e}\n{tb}')
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": str(e),
                    "traceback": tb
                }).encode())
        elif self.path == '/search':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            try:
                videos = search_new_videos()
                self.wfile.write(json.dumps({
                    "count": len(videos),
                    "videos": [{"url": v["url"], "title": v["title"]} for v in videos[:20]]
                }).encode())
            except Exception as e:
                tb = traceback.format_exc()
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": str(e),
                    "traceback": tb
                }).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

def run_server():
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    port = int(os.getenv('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f'[BOOT] Server starting on port {port}')

    if os.getenv('RAILWAY_CRON'):
        print('[BOOT] RAILWAY_CRON detected, running pipeline...')
        try:
            run_pipeline()
            print('[BOOT] Pipeline completed')
        except Exception as e:
            tb = traceback.format_exc()
            print(f'[BOOT] Pipeline error: {e}\n{tb}')

    print(f'[BOOT] Server ready on port {port}')
    server.serve_forever()

if __name__ == '__main__':
    run_server()
