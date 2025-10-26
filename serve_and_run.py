# serve_and_run.py
import os, threading, time, traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
import main as job  # your bot's main()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self): self._ok()
    def do_HEAD(self): self._ok(b"")
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()
    def _ok(self, body=b"OK"):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

def serve():
    port = int(os.getenv("PORT", "8080"))
    HTTPServer(("", port), Handler).serve_forever()

def loop():
    interval = int(os.getenv("INTERVAL_SECONDS", "21600"))  # 6 hours
    while True:
        try:
            print("Running scheduled job...")
            ok = job.main()
            print(f"Job finished with ok={ok}")
        except Exception:
            print("Job crashed:\n", traceback.format_exc())
        time.sleep(interval)

if __name__ == "__main__":
    threading.Thread(target=serve, daemon=True).start()
    loop()
