from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import subprocess
import sys
import tempfile


HOST = "0.0.0.0"
PORT = 8000

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

INDEX_FILE = os.path.join(
    BASE_DIR,
    "index.html"
)


class PPaiServer(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        print(
            "[PPai Server]",
            format % args
        )

    def send_json(self, data, status=200):

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
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, OPTIONS"
        )

        self.send_header(
            "Content-Length",
            str(len(body))
        )

        self.end_headers()

        self.wfile.write(body)

    def send_file(self, path, content_type):

        try:

            with open(path, "rb") as f:
                data = f.read()

            self.send_response(200)

            self.send_header(
                "Content-Type",
                content_type
            )

            self.send_header(
                "Content-Length",
                str(len(data))
            )

            self.end_headers()

            self.wfile.write(data)

        except FileNotFoundError:

            self.send_json(
                {
                    "error":
                    "Không tìm thấy file."
                },
                404
            )

        except Exception as e:

            self.send_json(
                {
                    "error": str(e)
                },
                500
            )

    def read_json(self):

        try:

            length = int(
                self.headers.get(
                    "Content-Length",
                    0
                )
            )

            if length <= 0:
                return {}

            raw = self.rfile.read(
                length
            )

            return json.loads(
                raw.decode("utf-8")
            )

        except Exception:

            return None

    def do_OPTIONS(self):

        self.send_response(204)

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, OPTIONS"
        )

        self.end_headers()

    def do_GET(self):

        if self.path == "/":

            self.send_file(
                INDEX_FILE,
                "text/html; charset=utf-8"
            )

            return

        if self.path == "/api":

            self.send_json(
                {
                    "name": "PPai",
                    "status": "online",
                    "python": sys.version,
                    "api": [
                        "/ai",
                        "/run"
                    ]
                }
            )

            return

        self.send_json(
            {
                "error":
                "Endpoint không tồn tại."
            },
            404
        )

    def do_POST(self):

        if self.path == "/ai":

            data = self.read_json()

            if data is None:

                self.send_json(
                    {
                        "error":
                        "JSON không hợp lệ."
                    },
                    400
                )

                return

            self.ai(data)

            return

        if self.path == "/run":

            data = self.read_json()

            if data is None:

                self.send_json(
                    {
                        "error":
                        "JSON không hợp lệ."
                    },
                    400
                )

                return

            self.run_python(data)

            return

        self.send_json(
            {
                "error":
                "Endpoint không tồn tại."
            },
            404
        )

    def ai(self, data):

        message = data.get(
            "message",
            ""
        )

        code = data.get(
            "code",
            ""
        )

        if not isinstance(
            message,
            str
        ):

            message = ""

        if not isinstance(
            code,
            str
        ):

            code = ""

        ai_file = os.path.join(
            BASE_DIR,
            "ai.py"
        )

        if not os.path.isfile(
            ai_file
        ):

            self.send_json(
                {
                    "error":
                    "Không tìm thấy ai.py."
                },
                500
            )

            return

        payload = json.dumps(
            {
                "message": message,
                "code": code
            },
            ensure_ascii=False
        )

        try:

            process = subprocess.run(
                [
                    sys.executable,
                    ai_file
                ],

                input=payload,

                capture_output=True,

                text=True,

                encoding="utf-8",

                errors="replace",

                timeout=30
            )

            if process.returncode != 0:

                self.send_json(
                    {
                        "error":
                        process.stderr.strip()
                    },
                    500
                )

                return

            self.send_json(
                {
                    "response":
                    process.stdout.strip()
                }
            )

        except subprocess.TimeoutExpired:

            self.send_json(
                {
                    "error":
                    "AI xử lý quá lâu."
                },
                504
            )

        except Exception as e:

            self.send_json(
                {
                    "error": str(e)
                },
                500
            )

    def run_python(self, data):

        code = data.get(
            "code",
            ""
        )

        if not isinstance(
            code,
            str
        ):

            self.send_json(
                {
                    "error":
                    "Code phải là chuỗi."
                },
                400
            )

            return

        if not code.strip():

            self.send_json(
                {
                    "output": ""
                }
            )

            return

        temp_file = None

        try:

            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py",
                prefix="ppai_",
                encoding="utf-8",
                delete=False
            ) as f:

                f.write(code)

                temp_file = f.name

            process = subprocess.run(
                [
                    sys.executable,
                    "-u",
                    temp_file
                ],

                capture_output=True,

                text=True,

                encoding="utf-8",

                errors="replace",

                timeout=10
            )

            output = process.stdout

            if process.stderr:

                output += process.stderr

            self.send_json(
                {
                    "output": output,
                    "returncode":
                    process.returncode
                }
            )

        except subprocess.TimeoutExpired:

            self.send_json(
                {
                    "error":
                    "Code chạy quá 10 giây."
                },
                408
            )

        except Exception as e:

            self.send_json(
                {
                    "error": str(e)
                },
                500
            )

        finally:

            if temp_file:

                try:
                    os.remove(
                        temp_file
                    )
                except Exception:
                    pass


def main():

    print()
    print("=" * 50)
    print("                    PPai")
    print("                Python AI Server")
    print("=" * 50)
    print()

    print(
        f"Server: http://127.0.0.1:{PORT}"
    )

    print(
        f"API:    http://127.0.0.1:{PORT}/api"
    )

    print()
    print(
        "Ctrl+C để dừng server."
    )
    print()

    server = ThreadingHTTPServer(
        (HOST, PORT),
        PPaiServer
    )

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print()
        print(
            "[PPai] Đang dừng server..."
        )

    finally:

        server.server_close()

        print(
            "[PPai] Server đã dừng."
        )


if __name__ == "__main__":
    main()
