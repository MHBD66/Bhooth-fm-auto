import os
import sys
import json
import traceback
import threading
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass
try:
    sys.stderr.reconfigure(line_buffering=True)
except Exception:
    pass

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())
        elif self.path == '/run':
            self._handle_run()
        elif self.path == '/search':
            self._handle_search()
        else:
            self.send_response(404)
            self.end_headers()

    def _handle_run(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        try:
            from main import run_pipeline
            print('Pipeline triggered via /run')
            success = run_pipeline()
            self.wfile.write(json.dumps({
                "status": "success" if success else "failed"
            }).encode())
        except Exception as e:
            tb = traceback.format_exc()
            print(f'Pipeline error: {e}\n{tb}')
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode())

    def _handle_search(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        try:
            from search import search_new_videos
            videos = search_new_videos()
            self.wfile.write(json.dumps({
                "count": len(videos),
                "videos": [{"url": v["url"], "title": v["title"]} for v in videos[:20]]
            }).encode())
        except Exception as e:
            tb = traceback.format_exc()
            print(f'Search error: {e}\n{tb}')
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode())

    def log_message(self, format, *args):
        pass

def run_server():
    port = int(os.getenv('PORT', 8080))
    print(f'[BOOT] Starting server on port {port}', flush=True)

    try:
        server = HTTPServer(('0.0.0.0', port), HealthHandler)
        print(f'[BOOT] Server listening on 0.0.0.0:{port}', flush=True)
    except Exception as e:
        print(f'[BOOT] Failed to bind: {e}', flush=True)
        sys.exit(1)

    if os.getenv('RAILWAY_CRON'):
        print('[BOOT] RAILWAY_CRON set, launching pipeline in background...', flush=True)
        def _run():
            try:
                from main import run_pipeline
                run_pipeline()
                print('[BOOT] Pipeline done', flush=True)
            except Exception as e:
                print(f'[BOOT] Pipeline error: {e}', flush=True)
        t = threading.Thread(target=_run, daemon=True)
        t.start()

    print('[BOOT] Ready', flush=True)
    server.serve_forever()

if __name__ == '__main__':
    run_server()
