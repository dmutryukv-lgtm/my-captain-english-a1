from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
import json
import os

from excel_manager import ExcelDB
from learning_engine import LearningEngine


# ============================================================
# 1. ОСНОВНА ПАПКА ПРОЄКТУ
# ============================================================

BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# 2. ПАПКА WEB
# ============================================================

WEB_DIR = BASE_DIR / "web"


# ============================================================
# 3. EXCEL
# ============================================================
# Excel знаходиться ПОРУЧ із my_captain.py
#
# MY_CAPTAIN_ENGLISH_FINAL/
# ├── my_captain.py
# ├── excel_manager.py
# ├── learning_engine.py
# ├── requirements.txt
# ├── My_Captain_English_A1.xlsx
# └── web/
#
# Тому використовуємо BASE_DIR, а НЕ BASE_DIR.parent
# ============================================================

EXCEL_FILE = BASE_DIR / "My_Captain_English_A1.xlsx"


# ============================================================
# 4. СЕРВЕР
# ============================================================

HOST = "0.0.0.0"

PORT = int(os.environ.get("PORT", "10000"))


# ============================================================
# 5. ПЕРЕВІРКА ФАЙЛІВ
# ============================================================

print("=" * 60)
print("MY CAPTAIN ENGLISH")
print("=" * 60)

print("BASE_DIR:", BASE_DIR)
print("WEB_DIR:", WEB_DIR)
print("EXCEL_FILE:", EXCEL_FILE)

print("Excel exists:", EXCEL_FILE.exists())
print("Web exists:", WEB_DIR.exists())

if not EXCEL_FILE.exists():
    raise FileNotFoundError(
        f"Excel файл не знайдено: {EXCEL_FILE}"
    )

if not WEB_DIR.exists():
    raise FileNotFoundError(
        f"Папку web не знайдено: {WEB_DIR}"
    )


# ============================================================
# 6. ПІДКЛЮЧЕННЯ EXCEL
# ============================================================

db = ExcelDB(EXCEL_FILE)

engine = LearningEngine(db)


# ============================================================
# 7. HTTP HANDLER
# ============================================================

class Handler(SimpleHTTPRequestHandler):

    # --------------------------------------------------------
    # JSON ВІДПОВІДЬ
    # --------------------------------------------------------

    def _send_json(self, data, status=200):

        body = json.dumps(
            data,
            ensure_ascii=False
        ).encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(body))
        )

        self.send_header(
            "Cache-Control",
            "no-store"
        )

        self.end_headers()

        self.wfile.write(body)

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    def do_GET(self):

        parsed = urlparse(self.path)

        path = parsed.path

        # ----------------------------------------------------
        # ГОЛОВНА СТОРІНКА
        # ----------------------------------------------------

        if path == "/":

            self.path = "/index.html"

            return super().do_GET()

        # ----------------------------------------------------
        # API DASHBOARD
        # ----------------------------------------------------

        if path == "/api/dashboard":

            try:

                result = engine.dashboard()

                return self._send_json({
                    "ok": True,
                    "data": result
                })

            except Exception as e:

                return self._send_json({
                    "ok": False,
                    "error": str(e)
                }, 500)

        # ----------------------------------------------------
        # API LESSONS
        # ----------------------------------------------------

        if path == "/api/lessons":

            try:

                result = engine.lessons()

                return self._send_json({
                    "ok": True,
                    "data": result
                })

            except Exception as e:

                return self._send_json({
                    "ok": False,
                    "error": str(e)
                }, 500)

        # ----------------------------------------------------
        # API WORDS
        # ----------------------------------------------------

        if path == "/api/words":

            try:

                result = engine.words()

                return self._send_json({
                    "ok": True,
                    "data": result
                })

            except Exception as e:

                return self._send_json({
                    "ok": False,
                    "error": str(e)
                }, 500)

        # ----------------------------------------------------
        # API PHRASES
        # ----------------------------------------------------

        if path == "/api/phrases":

            try:

                result = engine.phrases()

                return self._send_json({
                    "ok": True,
                    "data": result
                })

            except Exception as e:

                return self._send_json({
                    "ok": False,
                    "error": str(e)
                }, 500)

        # ----------------------------------------------------
        # API GRAMMAR
        # ----------------------------------------------------

        if path == "/api/grammar":

            try:

                result = engine.grammar()

                return self._send_json({
                    "ok": True,
                    "data": result
                })

            except Exception as e:

                return self._send_json({
                    "ok": False,
                    "error": str(e)
                }, 500)

        # ----------------------------------------------------
        # API LISTENING
        # ----------------------------------------------------

        if path == "/api/listening":

            try:

                result = engine.listening()

                return self._send_json({
                    "ok": True,
                    "data": result
                })

            except Exception as e:

                return self._send_json({
                    "ok": False,
                    "error": str(e)
                }, 500)

        # ----------------------------------------------------
        # API SPEAKING
        # ----------------------------------------------------

        if path == "/api/speaking":

            try:

                result = engine.speaking()

                return self._send_json({
                    "ok": True,
                    "data": result
                })

            except Exception as e:

                return self._send_json({
                    "ok": False,
                    "error": str(e)
                }, 500)

        # ----------------------------------------------------
        # API ACHIEVEMENTS
        # ----------------------------------------------------

        if path == "/api/achievements":

            try:

                result = engine.achievements()

                return self._send_json({
                    "ok": True,
                    "data": result
                })

            except Exception as e:

                return self._send_json({
                    "ok": False,
                    "error": str(e)
                }, 500)

        # ----------------------------------------------------
        # API SETTINGS
        # ----------------------------------------------------

        if path == "/api/settings":

            try:

                result = engine.settings()

                return self._send_json({
                    "ok": True,
                    "data": result
                })

            except Exception as e:

                return self._send_json({
                    "ok": False,
                    "error": str(e)
                }, 500)

        # ----------------------------------------------------
        # ВСІ ІНШІ ЗАПИТИ
        # ----------------------------------------------------

        try:

            self.directory = str(WEB_DIR)

            if path.startswith("/web/"):

                self.path = path[4:]

            return super().do_GET()

        except Exception as e:

            return self._send_json({
                "ok": False,
                "error": str(e)
            }, 500)

    # --------------------------------------------------------
    # ЛОГУВАННЯ
    # --------------------------------------------------------

    def log_message(self, format, *args):

        print(
            "[WEB]",
            format % args
        )


# ============================================================
# 8. ЗАПУСК СЕРВЕРА
# ============================================================

def main():

    print()
    print("=" * 60)
    print("MY CAPTAIN ENGLISH SERVER")
    print("=" * 60)

    print("Host:", HOST)
    print("Port:", PORT)
    print("Excel:", EXCEL_FILE)
    print("Excel exists:", EXCEL_FILE.exists())
    print("Web:", WEB_DIR)

    print()
    print(
        f"Server running on http://{HOST}:{PORT}"
    )

    print("=" * 60)

    server = ThreadingHTTPServer(
        (HOST, PORT),
        Handler
    )

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print()
        print("Server stopped.")

    finally:

        server.server_close()


# ============================================================
# 9. START
# ============================================================

if __name__ == "__main__":

    main()
