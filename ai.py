import sys
import json
import re
import ast
import traceback


APP_NAME = "PPai"


# =========================================================
# UTILITY
# =========================================================

def clean(text):
    if not isinstance(text, str):
        return ""
    return text.strip()


def extract_code(text):
    """
    Lấy code từ:
    ```python
    print("Hello")
    ```
    """

    pattern = r"```(?:python|py)?\s*([\s\S]*?)```"

    match = re.search(
        pattern,
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1).strip()

    return None


def detect_python(code):
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as error:
        return False, error


# =========================================================
# CODE ANALYSIS
# =========================================================

def explain_code(code):

    if not code.strip():
        return "Không có code để giải thích."

    try:
        tree = ast.parse(code)
    except SyntaxError as error:
        return (
            "Code đang có lỗi cú pháp.\n\n"
            f"Dòng: {error.lineno}\n"
            f"Vấn đề: {error.msg}"
        )

    result = []

    result.append(
        "## Phân tích Python"
    )

    result.append("")

    functions = []
    classes = []
    imports = []
    variables = []

    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef):
            functions.append(
                node.name
            )

        elif isinstance(node, ast.AsyncFunctionDef):
            functions.append(
                node.name
            )

        elif isinstance(node, ast.ClassDef):
            classes.append(
                node.name
            )

        elif isinstance(node, ast.Import):
            for item in node.names:
                imports.append(
                    item.name
                )

        elif isinstance(node, ast.ImportFrom):

            if node.module:
                imports.append(
                    node.module
                )

        elif isinstance(node, ast.Assign):

            for target in node.targets:

                if isinstance(
                    target,
                    ast.Name
                ):
                    variables.append(
                        target.id
                    )

    if imports:

        result.append(
            "**Thư viện:** "
            + ", ".join(
                sorted(set(imports))
            )
        )

    if functions:

        result.append(
            "**Hàm:** "
            + ", ".join(
                sorted(set(functions))
            )
        )

    if classes:

        result.append(
            "**Class:** "
            + ", ".join(
                sorted(set(classes))
            )
        )

    if variables:

        result.append(
            "**Biến:** "
            + ", ".join(
                sorted(set(variables))
            )
        )

    result.append("")

    result.append(
        "### Code"
    )

    result.append("")

    result.append(
        "```python\n"
        + code
        + "\n```"
    )

    return "\n".join(result)


# =========================================================
# SYNTAX CHECK
# =========================================================

def check_code(code):

    if not code.strip():

        return (
            "Không có code để kiểm tra."
        )

    try:

        ast.parse(code)

        return (
            "Không phát hiện lỗi cú pháp "
            "Python cơ bản."
        )

    except SyntaxError as error:

        line = error.lineno or "?"

        column = error.offset or "?"

        message = error.msg or "SyntaxError"

        return (
            "## Lỗi Python\n\n"
            f"- Dòng: `{line}`\n"
            f"- Cột: `{column}`\n"
            f"- Lỗi: `{message}`"
        )


# =========================================================
# CODE GENERATORS
# =========================================================

def code_calculator():

    return '''a = float(input("Số thứ nhất: "))
b = float(input("Số thứ hai: "))

print("Tổng:", a + b)
print("Hiệu:", a - b)
print("Tích:", a * b)

if b != 0:
    print("Thương:", a / b)
else:
    print("Không thể chia cho 0.")'''


def code_hello():

    return '''name = input("Tên của bạn: ")

print("Xin chào,", name)
print("Chào mừng đến với PPai!")'''


def code_fibonacci():

    return '''n = int(input("Nhập số lượng phần tử: "))

a = 0
b = 1

for _ in range(n):
    print(a, end=" ")
    a, b = b, a + b

print()'''


def code_prime():

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


def code_guess():

    return '''import random

number = random.randint(1, 100)

print("Tao đã chọn một số từ 1 đến 100.")

while True:

    try:
        guess = int(input("Đoán số: "))

    except ValueError:
        print("Hãy nhập số.")
        continue

    if guess < number:
        print("Lớn hơn.")

    elif guess > number:
        print("Nhỏ hơn.")

    else:
        print("Chính xác!")
        break'''


def code_factorial():

    return '''n = int(input("Nhập n: "))

result = 1

for i in range(1, n + 1):
    result *= i

print("Giai thừa:", result)'''


def code_password():

    return '''password = "123456"

while True:

    value = input("Mật khẩu: ")

    if value == password:
        print("Đăng nhập thành công!")
        break

    print("Sai mật khẩu.")'''


def generate_code(message):

    text = message.lower()

    if (
        "máy tính" in text
        or "calculator" in text
        or "tính toán" in text
    ):
        return code_calculator()

    if "fibonacci" in text:
        return code_fibonacci()

    if (
        "số nguyên tố" in text
        or "prime" in text
    ):
        return code_prime()

    if (
        "đoán số" in text
        or "guess game" in text
    ):
        return code_guess()

    if (
        "giai thừa" in text
        or "factorial" in text
    ):
        return code_factorial()

    if (
        "mật khẩu" in text
        or "password" in text
    ):
        return code_password()

    if (
        "hello" in text
        or "xin chào" in text
    ):
        return code_hello()

    return None


# =========================================================
# INTENT DETECTION
# =========================================================

def wants_explanation(text):

    words = [
        "giải thích",
        "giải nghĩa",
        "explain",
        "phân tích code"
    ]

    return any(
        word in text.lower()
        for word in words
    )


def wants_fix(text):

    words = [
        "sửa lỗi",
        "sửa code",
        "debug",
        "fix code",
        "fix lỗi",
        "lỗi code"
    ]

    return any(
        word in text.lower()
        for word in words
    )


def wants_check(text):

    words = [
        "kiểm tra code",
        "check code",
        "kiểm tra lỗi",
        "có lỗi không",
        "syntax"
    ]

    return any(
        word in text.lower()
        for word in words
    )


def wants_code(text):

    words = [
        "viết code",
        "tạo code",
        "viết chương trình",
        "tạo chương trình",
        "code python",
        "lập trình",
        "python"
    ]

    return any(
        word in text.lower()
        for word in words
    )


# =========================================================
# FIX SIMPLE PYTHON
# =========================================================

def try_fix(code):

    if not code.strip():
        return None

    fixed = code

    # Một số lỗi cực cơ bản

    fixed = fixed.replace(
        "Print(",
        "print("
    )

    fixed = fixed.replace(
        "Input(",
        "input("
    )

    fixed = fixed.replace(
        "Truee",
        "True"
    )

    fixed = fixed.replace(
        "Falsee",
        "False"
    )

    fixed = fixed.replace(
        "Nonee",
        "None"
    )

    try:

        ast.parse(fixed)

        if fixed != code:
            return fixed

    except SyntaxError:
        pass

    return None


# =========================================================
# RESPONSE
# =========================================================

def response(message, current_code):

    message = clean(message)
    current_code = clean(current_code)

    if not message:

        return (
            "Mày chưa nhập yêu cầu."
        )

    # -------------------------
    # EXPLAIN
    # -------------------------

    if wants_explanation(message):

        code = current_code

        extracted = extract_code(
            message
        )

        if extracted:
            code = extracted

        if not code:

            return (
                "Mày chưa đưa code để tao "
                "phân tích."
            )

        return explain_code(code)

    # -------------------------
    # CHECK
    # -------------------------

    if wants_check(message):

        code = current_code

        extracted = extract_code(
            message
        )

        if extracted:
            code = extracted

        return check_code(code)

    # -------------------------
    # FIX
    # -------------------------

    if wants_fix(message):

        code = current_code

        extracted = extract_code(
            message
        )

        if extracted:
            code = extracted

        if not code:

            return (
                "Đưa code cần sửa vào editor "
                "hoặc gửi trong tin nhắn."
            )

        valid, error = detect_python(
            code
        )

        if valid:

            return (
                "Tao không thấy lỗi cú pháp "
                "Python cơ bản.\n\n"
                "Nếu chương trình vẫn lỗi, "
                "có thể đó là lỗi logic hoặc "
                "lỗi khi chạy."
            )

        fixed = try_fix(code)

        if fixed:

            return (
                "## Tao tìm thấy lỗi\n\n"
                "Bản sửa:\n\n"
                "```python\n"
                + fixed
                + "\n```"
            )

        return (
            "## Lỗi cú pháp\n\n"
            f"Dòng `{error.lineno}`: "
            f"{error.msg}\n\n"
            "Code hiện tại:\n\n"
            "```python\n"
            + code
            + "\n```"
        )

    # -------------------------
    # GENERATE
    # -------------------------

    if wants_code(message):

        generated = generate_code(
            message
        )

        if generated:

            return (
                "## Python\n\n"
                "```python\n"
                + generated
                + "\n```"
            )

        return (
            "Tao hiểu là mày muốn code Python.\n\n"
            "PPai hiện hỗ trợ tạo mẫu cho:\n\n"
            "- Máy tính\n"
            "- Fibonacci\n"
            "- Số nguyên tố\n"
            "- Game đoán số\n"
            "- Giai thừa\n"
            "- Mật khẩu\n"
            "- Hello World"
        )

    # -------------------------
    # GENERAL
    # -------------------------

    return (
        "## PPai\n\n"
        "Đã nhận:\n\n"
        + message
        + "\n\n"
        "Đây là bản AI local của PPai. "
        "Nó đang xử lý bằng Python mà không "
        "cần dịch vụ AI bên ngoài."
    )


# =========================================================
# MAIN
# =========================================================

def main():

    try:

        raw = sys.stdin.read()

        if not raw.strip():

            print(
                "PPai: Không nhận được dữ liệu."
            )

            return

        data = json.loads(raw)

        message = data.get(
            "message",
            ""
        )

        code = data.get(
            "code",
            ""
        )

        result = response(
            message,
            code
        )

        print(result)

    except json.JSONDecodeError:

        print(
            "PPai: JSON không hợp lệ."
        )

    except Exception as error:

        print(
            "PPai Error:",
            str(error)
        )

        traceback.print_exc(
            file=sys.stderr
        )


if __name__ == "__main__":
    main()
