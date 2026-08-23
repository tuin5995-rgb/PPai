import sys
import json
import re


APP_NAME = "PPai"


def clean_message(message):
    return message.strip()


def extract_code(message):
    """
    Tìm code Python nằm trong markdown:
    ```python
    ...
    ```
    """

    match = re.search(
        r"```(?:python|py)?\s*([\s\S]*?)```",
        message,
        re.IGNORECASE
    )

    if match:
        return match.group(1).strip()

    return None


def explain_code(code):
    if not code.strip():
        return "Không có code để giải thích."

    lines = code.splitlines()
    result = []

    for index, line in enumerate(lines, 1):

        text = line.strip()

        if not text:
            continue

        if text.startswith("#"):
            result.append(
                f"Dòng {index}: chú thích."
            )

        elif text.startswith("print("):
            result.append(
                f"Dòng {index}: in dữ liệu ra màn hình."
            )

        elif text.startswith("input("):
            result.append(
                f"Dòng {index}: nhận dữ liệu từ người dùng."
            )

        elif text.startswith("import "):
            result.append(
                f"Dòng {index}: nhập một module/thư viện."
            )

        elif text.startswith("from "):
            result.append(
                f"Dòng {index}: nhập thành phần từ một module."
            )

        elif text.startswith("def "):
            name = text[4:].split("(")[0]

            result.append(
                f"Dòng {index}: định nghĩa hàm `{name}`."
            )

        elif text.startswith("class "):
            name = text[6:].split("(")[0].split(":")[0]

            result.append(
                f"Dòng {index}: định nghĩa class `{name}`."
            )

        elif text.startswith("if "):
            result.append(
                f"Dòng {index}: kiểm tra điều kiện."
            )

        elif text.startswith("elif "):
            result.append(
                f"Dòng {index}: kiểm tra điều kiện khác."
            )

        elif text.startswith("else:"):
            result.append(
                f"Dòng {index}: nhánh còn lại của điều kiện."
            )

        elif text.startswith("for "):
            result.append(
                f"Dòng {index}: tạo vòng lặp `for`."
            )

        elif text.startswith("while "):
            result.append(
                f"Dòng {index}: tạo vòng lặp `while`."
            )

        elif text.startswith("return "):
            result.append(
                f"Dòng {index}: trả về một giá trị từ hàm."
            )

        elif "=" in text and "==" not in text:

            result.append(
                f"Dòng {index}: gán giá trị cho biến."
            )

        else:

            result.append(
                f"Dòng {index}: thực hiện `{text}`."
            )

    return "\n".join(result)


def generate_calculator():

    return '''a = float(input("Số thứ nhất: "))
b = float(input("Số thứ hai: "))

print("Tổng:", a + b)
print("Hiệu:", a - b)
print("Tích:", a * b)

if b != 0:
    print("Thương:", a / b)
else:
    print("Không thể chia cho 0.")'''


def generate_fibonacci():

    return '''n = int(input("Nhập số lượng phần tử: "))

a = 0
b = 1

for _ in range(n):
    print(a, end=" ")
    a, b = b, a + b

print()'''


def generate_guess_game():

    return '''import random

number = random.randint(1, 100)

print("Tao đã chọn một số từ 1 đến 100.")

while True:
    try:
        guess = int(input("Đoán số: "))
    except ValueError:
        print("Hãy nhập một số.")
        continue

    if guess < number:
        print("Lớn hơn.")
    elif guess > number:
        print("Nhỏ hơn.")
    else:
        print("Đúng rồi!")
        break'''


def generate_hello():

    return '''name = input("Tên của bạn: ")

print("Xin chào,", name)
print("Chào mừng đến với PPai!")'''


def generate_prime():

    return '''n = int(input("Nhập số: "))

if n < 2:
    print("Không phải số nguyên tố.")
else:
    is_prime = True

    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            is_prime = False
            break

    if is_prime:
        print("Là số nguyên tố.")
    else:
        print("Không phải số nguyên tố.")'''


def generate_code(message):

    text = message.lower()

    if (
        "máy tính" in text
        or "calculator" in text
        or "tính toán" in text
    ):
        return generate_calculator()

    if "fibonacci" in text:
        return generate_fibonacci()

    if (
        "đoán số" in text
        or "guess game" in text
    ):
        return generate_guess_game()

    if (
        "hello" in text
        or "xin chào" in text
        or "chào" in text
    ):
        return generate_hello()

    if (
        "số nguyên tố" in text
        or "prime" in text
    ):
        return generate_prime()

    return None


def is_explain_request(message):

    text = message.lower()

    words = [
        "giải thích",
        "giải nghĩa",
        "explain",
        "giải thích code"
    ]

    return any(
        word in text
        for word in words
    )


def is_fix_request(message):

    text = message.lower()

    words = [
        "sửa lỗi",
        "sửa code",
        "fix",
        "debug",
        "lỗi code",
        "sửa giúp"
    ]

    return any(
        word in text
        for word in words
    )


def is_code_request(message):

    text = message.lower()

    words = [
        "viết code",
        "tạo code",
        "viết chương trình",
        "tạo chương trình",
        "code python",
        "python",
        "lập trình"
    ]

    return any(
        word in text
        for word in words
    )


def build_response(message, current_code):

    message = clean_message(message)

    if not message:
        return "Mày chưa nhập yêu cầu."

    # -----------------------------
    # EXPLAIN
    # -----------------------------

    if is_explain_request(message):

        if current_code.strip():

            explanation = explain_code(
                current_code
            )

            return (
                "## Giải thích code\n\n"
                + explanation
            )

        extracted = extract_code(message)

        if extracted:

            explanation = explain_code(
                extracted
            )

            return (
                "## Giải thích code\n\n"
                + explanation
            )

        return (
            "Mày chưa đưa code cho tao giải thích."
        )

    # -----------------------------
    # FIX
    # -----------------------------

    if is_fix_request(message):

        if current_code.strip():

            return (
                "## Phân tích code\n\n"
                "Tao đã nhận đoạn code hiện tại "
                "trong editor.\n\n"
                "Code:\n\n"
                "```python\n"
                + current_code
                + "\n```\n\n"
                "Bản PPai local hiện tại chưa có "
                "model thật để phân tích lỗi tự động. "
                "Phần này sẽ được kết nối với AI model "
                "ở phiên bản sau."
            )

        extracted = extract_code(message)

        if extracted:

            return (
                "Tao đã nhận code:\n\n"
                "```python\n"
                + extracted
                + "\n```\n\n"
                "Hiện tại PPai local chưa có model "
                "thật để debug tự động."
            )

        return (
            "Hãy đưa code cần sửa vào editor "
            "hoặc trong tin nhắn."
        )

    # -----------------------------
    # GENERATE CODE
    # -----------------------------

    if is_code_request(message):

        generated = generate_code(
            message
        )

        if generated:

            return (
                "## Code Python\n\n"
                "```python\n"
                + generated
                + "\n```\n\n"
                "Mày có thể copy hoặc chạy trực tiếp "
                "đoạn code này."
            )

        return (
            "Tao hiểu là mày muốn viết Python.\n\n"
            "Hiện tại PPai local có thể tạo một số "
            "chương trình mẫu như:\n\n"
            "- Máy tính\n"
            "- Fibonacci\n"
            "- Game đoán số\n"
            "- Kiểm tra số nguyên tố\n"
            "- Chương trình Hello\n\n"
            "AI model thật sẽ được thêm vào sau."
        )

    # -----------------------------
    # GENERAL
    # -----------------------------

    return (
        "## PPai\n\n"
        "Tao đã nhận yêu cầu:\n\n"
        "> "
        + message.replace("\n", "\n> ")
        + "\n\n"
        "PPai hiện đang chạy ở chế độ AI local "
        "thử nghiệm."
    )


def main():

    try:

        raw = sys.stdin.read()

        if not raw.strip():

            print(
                "Không nhận được dữ liệu."
            )

            return

        data = json.loads(raw)

        message = data.get(
            "message",
            ""
        )

        current_code = data.get(
            "code",
            ""
        )

        if not isinstance(
            message,
            str
        ):
            message = ""

        if not isinstance(
            current_code,
            str
        ):
            current_code = ""

        response = build_response(
            message,
            current_code
        )

        print(response)

    except json.JSONDecodeError:

        print(
            "PPai AI: dữ liệu JSON không hợp lệ."
        )

    except Exception as error:

        print(
            "PPai AI Error: "
            + str(error)
        )


if __name__ == "__main__":
    main()
