from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import subprocess
import sys
import tempfile


HOST = "127.0.0.1"
PORT = 8000

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(BASE_DIR, "index.html")


class PPaiServer(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        print("[PPai]", format % args)

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
            "Content-Length",
            str(len(body))
        )

        self.send_header(
            "Cache-Control",
            "no-cache"
        )

        self.end_headers()

        self.wfile.write(body)

    def send_file(self, path, content_type):

        try:

            with open(path, "rb") as file:
                data = file.read()

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

            self.send_error(
                404,
                "File không tồn tại."
            )

        except Exception as error:

            self.send_error(
                500,
                str(error)
            )

    def read_json(self):

        try:

            length = int(
                self.headers.get(
                    "Content-Length",
                    "0"
                )
            )

            if length <= 0:
                return None

            raw = self.rfile.read(length)

            return json.loads(
                raw.decode("utf-8")
            )

        except Exception:

            return None

    def do_GET(self):

        if self.path in ["/", "/index.html"]:

            self.send_file(
                INDEX_FILE,
                "text/html; charset=utf-8"
            )

            return

        if self.path == "/favicon.ico":

            self.send_response(204)
            self.end_headers()

            return

        self.send_json(
            {
                "error": "Không tìm thấy trang."
            },
            404
        )

    def do_POST(self):

        if self.path == "/run":

            data = self.read_json()

            if data is None:

                self.send_json(
                    {
                        "error": "JSON không hợp lệ."
                    },
                    400
                )

                return

            self.run_python(data)

            return

        if self.path == "/ai":

            data = self.read_json()

            if data is None:

                self.send_json(
                    {
                        "error": "JSON không hợp lệ."
                    },
                    400
                )

                return

            self.run_ai(data)

            return

        self.send_json(
            {
                "error": "API không tồn tại."
            },
            404
        )

    # --------------------------------
    # RUN PYTHON
    # --------------------------------

    def run_python(self, data):

        code = data.get("code", "")

        if not isinstance(code, str):

            self.send_json(
                {
                    "error": "Code phải là chuỗi."
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

        temp_path = None

        try:

            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py",
                prefix="ppai_",
                delete=False,
                encoding="utf-8"
            ) as file:

                file.write(code)
                temp_path = file.name

            print("[RUN] Python")

            process = subprocess.Popen(
                [
                    sys.executable,
                    "-u",
                    temp_path
                ],

                stdout=subprocess.PIPE,

                stderr=subprocess.STDOUT,

                stdin=subprocess.DEVNULL,

                text=True,

                encoding="utf-8",

                errors="replace"
            )

            try:

                output, _ = process.communicate(
                    timeout=10
                )

            except subprocess.TimeoutExpired:

                process.kill()

                output, _ = process.communicate()

                output += (
                    "\n\n"
                    "[PPai] Chương trình đã bị dừng "
                    "vì chạy quá 10 giây."
                )

            self.send_json(
                {
                    "output": output,
                    "returncode": process.returncode
                }
            )

        except Exception as error:

            self.send_json(
                {
                    "error":
                        "Không thể chạy Python:\n"
                        + str(error)
                },
                500
            )

        finally:

            if temp_path:

                try:
                    os.remove(temp_path)

                except Exception:
                    pass

    # --------------------------------
    # AI
    # --------------------------------

    def run_ai(self, data):

        message = data.get(
            "message",
            ""
        )

        code = data.get(
            "code",
            ""
        )

        if not isinstance(message, str):

            self.send_json(
                {
                    "error":
                        "Message không hợp lệ."
                },
                400
            )

            return

        if not isinstance(code, str):

            code = ""

        if not message.strip():

            self.send_json(
                {
                    "error":
                        "Tin nhắn trống."
                },
                400
            )

            return

        ai_file = os.path.join(
            BASE_DIR,
            "ai.py"
        )

        if not os.path.exists(ai_file):

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

            print("[AI]", message)

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

                error = process.stderr.strip()

                if not error:
                    error = "ai.py trả về lỗi."

                self.send_json(
                    {
                        "error": error
                    },
                    500
                )

                return

            response = process.stdout.strip()

            self.send_json(
                {
                    "response": response
                }
            )

        except subprocess.TimeoutExpired:

            self.send_json(
                {
                    "error":
                        "PPai AI phản hồi quá lâu."
                },
                504
            )

        except Exception as error:

            self.send_json(
                {
                    "error":
                        "Không thể chạy AI:\n"
                        + str(error)
                },
                500
            )


def main():

    print()
    print("=" * 50)
    print("                 PPai")
    print("             Python AI IDE")
    print("=" * 50)
    print()
    print(
        f"Server đang chạy tại:"
    )
    print(
        f"http://{HOST}:{PORT}"
    )
    print()
    print(
        "Nhấn Ctrl+C để dừng server."
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
        print("[PPai] Đang dừng...")

    finally:

        server.server_close()

        print("[PPai] Server đã dừng.")


if __name__ == "__main__":
    main()
