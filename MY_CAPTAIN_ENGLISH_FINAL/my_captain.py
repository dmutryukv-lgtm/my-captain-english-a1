from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
import json
import os

from excel_manager import ExcelDB
from learning_engine import LearningEngine

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"
EXCEL_FILE = BASE_DIR.parent / "My_Captain_English_A1.xlsx"
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "10000"))

db = ExcelDB(EXCEL_FILE)
engine = LearningEngine(db)

class Handler(SimpleHTTPRequestHandler):
    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path):
        try:
            data = Path(path).read_bytes()
        except FileNotFoundError:
            self.send_error(404)
            return
        content_type = "text/html; charset=utf-8"
        if str(path).endswith(".css"):
            content_type = "text/css; charset=utf-8"
        elif str(path).endswith(".js"):
            content_type = "application/javascript; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/") or "/"

        try:
            if path == "/api/health":
                self._send_json({
                    "ok": True,
                    "app": "MY CAPTAIN ENGLISH",
                    "excel": str(EXCEL_FILE),
                    "excel_exists": EXCEL_FILE.exists()
                })
                return

            if path == "/api/dashboard":
                self._send_json(engine.dashboard())
                return

            if path == "/api/lessons":
                self._send_json(engine.lessons())
                return

            if path.startswith("/api/lesson/"):
                lesson_id = path.split("/")[-1]
                self._send_json(engine.lesson(lesson_id))
                return

            if path == "/api/words":
                self._send_json(engine.words())
                return

            if path == "/api/phrases":
                self._send_json(engine.phrases())
                return

            if path == "/api/grammar":
                self._send_json(engine.grammar())
                return

            if path == "/api/listening":
                self._send_json(engine.listening())
                return

            if path == "/api/speaking":
                self._send_json(engine.speaking())
                return

            if path == "/api/achievements":
                self._send_json(engine.achievements())
                return

            if path == "/api/settings":
                self._send_json(engine.settings())
                return

            if path == "/":
                path = "/index.html"

            safe = (WEB_DIR / path.lstrip("/")).resolve()
            if WEB_DIR.resolve() not in safe.parents and safe != WEB_DIR.resolve():
                self.send_error(403)
                return
            self._send_file(safe)

        except Exception as e:
            self._send_json({"ok": False, "error": str(e)}, 500)

    def do_POST(self):
        path = urlparse(self.path).path
        if not path.startswith("/api/"):
            self.send_error(404)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length else b"{}"
            data = json.loads(raw.decode("utf-8") or "{}")

            if path == "/api/activity":
                result = engine.record_activity(data)
                self._send_json(result)
                return

            if path == "/api/word-result":
                result = engine.record_word_result(data)
                self._send_json(result)
                return

            self.send_error(404)

        except Exception as e:
            self._send_json({"ok": False, "error": str(e)}, 500)

    def log_message(self, fmt, *args):
        print("[WEB]", fmt % args)

if __name__ == "__main__":
    print("======================================")
    print(" MY CAPTAIN ENGLISH")
    print("======================================")
    print("Excel:", EXCEL_FILE)
    print("Excel exists:", EXCEL_FILE.exists())
    print(f"Web: http://127.0.0.1:{PORT}")
    print("Stop: CTRL+C")
    print("======================================")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    server.serve_forever()
