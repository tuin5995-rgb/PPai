# PPai

**PPai** là một Python AI IDE chạy trên web, cho phép viết, chạy và hỗ trợ lập trình Python trực tiếp trong trình duyệt.

## Tính năng

* Trình soạn thảo Python trên web
* Chạy code Python trực tiếp
* Terminal hiển thị kết quả
* PPai AI hỗ trợ lập trình Python
* Giao diện IDE đơn giản
* HTML, CSS và JavaScript được gộp trong `index.html`
* Backend viết bằng Python
* Không cần Java

## Cấu trúc

```text
PPai/
├── index.html
├── server.py
├── ai.py
└── README.md
```

### `index.html`

Chứa toàn bộ:

* HTML
* CSS
* JavaScript
* Python editor
* Terminal
* Giao diện PPai AI

### `server.py`

Web server của PPai.

Nhiệm vụ:

* Phục vụ `index.html`
* Nhận code Python từ trình duyệt
* Chạy code Python
* Trả kết quả về terminal
* Kết nối giao diện với `ai.py`

### `ai.py`

Bộ xử lý AI của PPai.

Hiện tại đây là phiên bản thử nghiệm, có thể:

* Nhận yêu cầu từ người dùng
* Phân tích code cơ bản
* Giải thích code
* Tạo một số đoạn Python mẫu
* Sửa lỗi theo mô hình thử nghiệm

Sau này có thể kết nối model AI thực sự vào file này.

## Yêu cầu

Cần cài:

* Python 3.x
* Trình duyệt web hiện đại

Không cần:

* Java
* Node.js
* npm
* MinGW
* Framework frontend

## Chạy PPai

Mở terminal tại thư mục `PPai`:

```bash
python server.py
```

Sau đó mở:

```text
http://127.0.0.1:8000
```

PPai sẽ chạy trên máy local.

## Cách hoạt động

```text
Browser
   │
   │ HTTP
   ▼
server.py
   │
   ├── /run
   │      │
   │      ▼
   │   Python
   │
   └── /ai
          │
          ▼
        ai.py
```

## Chạy Python

Viết code trong `main.py` trên giao diện PPai rồi nhấn:

```text
▶ Run
```

PPai gửi code đến `server.py`.

`server.py` tạo file Python tạm thời, chạy bằng Python interpreter và trả kết quả về Terminal.

Có thể dùng:

```text
Ctrl + Enter
```

để chạy code nhanh.

## AI

Nhập yêu cầu vào khung **PPai AI**.

Ví dụ:

```text
viết chương trình fibonacci bằng Python
```

hoặc:

```text
giải thích code này
```

AI sẽ nhận cả yêu cầu và code hiện tại trong editor.

## Bảo mật

Phiên bản hiện tại được thiết kế chủ yếu để chạy **local**.

Không nên đưa `server.py` lên Internet công khai mà không bổ sung sandbox, giới hạn quyền process, giới hạn tài nguyên và các biện pháp bảo mật khác.

Việc cho người lạ gửi Python tùy ý đến server rồi chạy trực tiếp là cách khá hiệu quả để biến máy chủ thành đồ chơi của người lạ.

## Mục tiêu phát triển

PPai hướng tới một môi trường:

```text
Viết Python
     ↓
AI hỗ trợ
     ↓
Chạy code
     ↓
Xem lỗi
     ↓
AI phân tích lỗi
     ↓
Sửa code
     ↓
Chạy lại
```

Mục tiêu cuối cùng là tạo một **AI IDE Python chạy hoàn toàn trên web**, với giao diện đơn giản và cấu trúc project gọn.

## License

Dự án có thể được sử dụng, chỉnh sửa và phát triển tùy theo license được thêm vào repository.
