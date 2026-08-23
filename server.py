from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import subprocess
import sys
import os
import tempfile
import threading
import time


HOST = "127.0.0.1"
PORT = 8000

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(BASE_DIR, "index.html")


class PPaiServer(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        self.wfile.write(body)

    def send_html(self):
        try:
            with open(INDEX_FILE, "rb") as file:
                data = file.read()

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()

            self.wfile.write(data)

        except Exception as e:
            self.send_error(500, str(e))

    def do_GET(self):

        if self.path == "/" or self.path == "/index.html":
            self.send_html()
            return

        self.send_error(404, "Not Found")

    def do_POST(self):

        if self.path not in ["/run", "/ai"]:
            self.send_json(
                {"error": "API không tồn tại."},
                404
            )
            return

        try:
            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            raw_data = self.rfile.read(content_length)

            data = json.loads(
                raw_data.decode("utf-8")
            )

        except Exception as e:
            self.send_json(
                {"error": "Dữ liệu không hợp lệ: " + str(e)},
                400
            )
            return

        if self.path == "/run":
            self.run_python(data)

        elif self.path == "/ai":
            self.run_ai(data)

    def run_python(self, data):

        code = data.get("code", "")

        if not isinstance(code, str):
            self.send_json(
                {"error": "Code phải là chuỗi."},
                400
            )
            return

        if not code.strip():
            self.send_json(
                {"output": ""}
            )
            return

        temp_file = None

        try:

            # Tạo file Python tạm thời
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py",
                delete=False,
                encoding="utf-8"
            ) as file:

                file.write(code)
                temp_file = file.name

            # Chạy Python
            process = subprocess.Popen(
                [
                    sys.executable,
                    "-u",
                    temp_file
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
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
                    "\n\n[PPai] Chương trình vượt quá "
                    "10 giây và đã bị dừng."
                )

            if process.returncode != 0:

                self.send_json({
                    "output": output,
                    "returncode": process.returncode
                })

            else:

                self.send_json({
                    "output": output,
                    "returncode": 0
                })

        except Exception as e:

            self.send_json({
                "error": "Không thể chạy Python:\n" + str(e)
            }, 500)

        finally:

            if temp_file:

                try:
                    os.remove(temp_file)
                except Exception:
                    pass

    def run_ai(self, data):

        message = data.get("message", "")
        code = data.get("code", "")

        if not message:
            self.send_json(
                {"error": "Tin nhắn AI trống."},
                400
            )
            return

        # Hiện tại gọi ai.py.
        # ai.py sẽ nhận message + code qua stdin.
        ai_file = os.path.join(BASE_DIR, "ai.py")

        if not os.path.exists(ai_file):

            self.send_json({
                "response":
                    "Chưa tìm thấy ai.py. "
                    "Hãy tạo file ai.py trong repo PPai."
            })

            return

        try:

            payload = json.dumps({
                "message": message,
                "code": code
            }, ensure_ascii=False)

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

                self.send_json({
                    "error":
                        "AI bị lỗi:\n" +
                        process.stderr
                })

                return

            self.send_json({
                "response":
                    process.stdout.strip()
            })

        except subprocess.TimeoutExpired:

            self.send_json({
                "error":
                    "AI mất hơn 30 giây để phản hồi."
            })

        except Exception as e:

            self.send_json({
                "error":
                    "Không thể chạy AI: " +
                    str(e)
            })


def main():

    server = HTTPServer(
        (HOST, PORT),
        PPaiServer
    )

    print("=" * 45)
    print("PPai - Python AI IDE")
    print("=" * 45)
    print()
    print(f"Server: http://{HOST}:{PORT}")
    print()
    print("Đang chạy...")
    print("Nhấn Ctrl+C để dừng.")
    print()

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print("\nĐang dừng PPai...")

    finally:
        server.server_close()


if __name__ == "__main__":
    main()
