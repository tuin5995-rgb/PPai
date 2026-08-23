import sys
import json
import re


def get_python_help(message, code):
    text = message.lower()

    if "sửa" in text or "fix" in text or "lỗi" in text:
        if not code.strip():
            return "Mày chưa có code để sửa."

        return (
            "Tao đã nhận code.\n\n"
            "Code hiện tại:\n"
            "```python\n"
            + code +
            "\n```\n\n"
            "Bản AI thật sẽ phân tích lỗi và sửa trực tiếp đoạn code này."
        )

    if "giải thích" in text or "explain" in text:
        if not code.strip():
            return "Mày chưa có code để giải thích."

        return (
            "Code này có:\n\n"
            + explain_code(code)
        )

    if "hello" in text or "xin chào" in text:
        return "Xin chào. PPai AI đang hoạt động."

    if "python" in text:
        return (
            "Python đã sẵn sàng.\n\n"
            "Mày có thể yêu cầu:\n"
            "- Viết code\n"
            "- Sửa lỗi\n"
            "- Giải thích code\n"
            "- Tối ưu code\n"
            "- Tạo project"
        )

    return (
        "PPai AI đã nhận yêu cầu:\n\n"
        + message +
        "\n\n"
        "Hiện tại đây là AI thử nghiệm. "
        "Hãy kết nối model thật vào ai.py để AI có thể sinh code."
    )


def explain_code(code):
    lines = code.splitlines()

    result = []

    for number, line in enumerate(lines, 1):

        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith("#"):
            result.append(
                f"Dòng {number}: comment."
            )

        elif stripped.startswith("print("):
            result.append(
                f"Dòng {number}: in dữ liệu ra màn hình."
            )

        elif stripped.startswith("input("):
            result.append(
                f"Dòng {number}: nhận dữ liệu từ người dùng."
            )

        elif stripped.startswith("def "):
            name = stripped[4:].split("(")[0]

            result.append(
                f"Dòng {number}: định nghĩa hàm `{name}`."
            )

        elif stripped.startswith("if "):
            result.append(
                f"Dòng {number}: kiểm tra điều kiện."
            )

        elif stripped.startswith("for "):
            result.append(
                f"Dòng {number}: tạo vòng lặp `for`."
            )

        elif stripped.startswith("while "):
            result.append(
                f"Dòng {number}: tạo vòng lặp `while`."
            )

        elif "import " in stripped:
            result.append(
                f"Dòng {number}: import thư viện/module."
            )

        elif "=" in stripped and not "==" in stripped:
            result.append(
                f"Dòng {number}: gán giá trị cho biến."
            )

        else:
            result.append(
                f"Dòng {number}: `{stripped}`"
            )

    if not result:
        return "Code trống."

    return "\n".join(result)


def generate_basic_code(message):

    text = message.lower()

    if "hello" in text or "xin chào" in text:
        return '''print("Hello, world!")'''

    if "máy tính" in text or "calculator" in text:
        return '''a = float(input("Số thứ nhất: "))
b = float(input("Số thứ hai: "))

print("Tổng:", a + b)
print("Hiệu:", a - b)
print("Tích:", a * b)

if b != 0:
    print("Thương:", a / b)
else:
    print("Không thể chia cho 0.")'''

    if "đoán số" in text:
        return '''import random

number = random.randint(1, 100)

print("Tao đã chọn một số từ 1 đến 100.")

while True:
    guess = int(input("Đoán: "))

    if guess < number:
        print("Lớn hơn.")
    elif guess > number:
        print("Nhỏ hơn.")
    else:
        print("Đúng!")
        break'''

    if "fibonacci" in text:
        return '''n = int(input("Nhập n: "))

a = 0
b = 1

for _ in range(n):
    print(a, end=" ")
    a, b = b, a + b'''

    return None


def process(data):

    message = data.get("message", "")
    code = data.get("code", "")

    if not isinstance(message, str):
        return "Yêu cầu không hợp lệ."

    generated = generate_basic_code(message)

    if generated:

        return (
            "Tao tạo cho mày đoạn Python này:\n\n"
            "```python\n"
            + generated +
            "\n```\n\n"
            "Có thể đưa thẳng vào editor."
        )

    return get_python_help(message, code)


def main():

    try:
        raw = sys.stdin.read()

        if not raw.strip():
            print("Không nhận được dữ liệu.")
            return

        data = json.loads(raw)

        result = process(data)

        print(result)

    except json.JSONDecodeError:
        print("Dữ liệu AI không phải JSON hợp lệ.")

    except Exception as e:
        print("PPai AI Error:", str(e))


if __name__ == "__main__":
    main()
