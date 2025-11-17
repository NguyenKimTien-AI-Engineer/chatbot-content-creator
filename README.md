# MekongAI Template - Hệ thống RAG Nâng cao

Một hệ thống Retrieval-Augmented Generation (RAG) cấp doanh nghiệp được thiết kế để xử lý tài liệu phức tạp và trả lời câu hỏi thông minh trên nhiều loại và kích thước tệp khác nhau.

## 🚀 Các tính năng chính

### Xử lý tài liệu nâng cao
- **Tệp nhỏ (< 10MB)**: Xử lý trực tiếp với chunking được tối ưu hóa và các hoạt động trong bộ nhớ
- **Tệp lớn (hơn 1000 trang)**: Xử lý streaming với chỉ mục phân cấp để tiết kiệm bộ nhớ
- **Phân tích nhiều tài liệu**: Xử lý song song với chỉ mục hợp nhất và tổng hợp thông tin từ nhiều tài liệu
- **Hỗ trợ định dạng**: PDF, DOCX, TXT, HTML, CSV, XLSX với khả năng OCR

### Trả lời câu hỏi thông minh
- **Tìm kiếm ngữ nghĩa**: Truy xuất dựa trên ngữ cảnh bằng cách sử dụng các phương pháp kết hợp (ngữ nghĩa + từ khóa + đồ thị)
- **Tìm kiếm toàn văn bản chính xác**: Tìm kiếm đa phương pháp bao gồm khớp chính xác, tìm kiếm mờ và các mẫu regex
- **Tác vụ tổng hợp**: Đếm và phân tích thống kê nâng cao với xác thực đa phương pháp
- **Tổng hợp thông tin từ nhiều tài liệu**: Tổng hợp thông tin từ nhiều tài liệu với xác minh tính nhất quán

### Tính năng doanh nghiệp
- **Kiến trúc có thể mở rộng**: Xử lý phân tán cho các bộ sưu tập tài liệu lớn
- **Hệ thống bộ nhớ đệm**: Bộ nhớ đệm đa lớp để có hiệu suất tối ưu
- **Phục hồi lỗi**: Xử lý lỗi mạnh mẽ với các cơ chế dự phòng
- **Giám sát hiệu suất**: Các chỉ số và tối ưu hóa theo thời gian thực

## 📚 Tài liệu

- **[Hướng dẫn chi tiết các chức năng](enhanced_system/docs/DETAILED_FUNCTIONS.md)**: Tài liệu kỹ thuật toàn diện về tất cả các thành phần của hệ thống
- **[Tối ưu hóa hiệu suất](enhanced_system/docs/PERFORMANCE_OPTIMIZATION.md)**: Cấu hình nâng cao và các phương pháp hay nhất về mở rộng quy mô
- **[Cấu trúc dự án](resources/docs/project_structure.md)**: Tổng quan đầy đủ về kiến trúc hệ thống

## 🛠 Cài đặt & Thiết lập

### Sao chép dự án
```shell
git clone https://github.com/mekongai/mekongai-template.git
```

---

## 🎯 Các trường hợp sử dụng nâng cao

### Hỏi và đáp trong các tệp nhỏ
**Nguyên tắc**: Tải trực tiếp với chunking đơn giản
- Toàn bộ tài liệu được tải vào bộ nhớ để truy cập nhanh
- Các đoạn có kích thước cố định (1000 token) với phần chồng lấp (200 token)
- Các hoạt động vector trong bộ nhớ để tìm kiếm tức thì
- Các mô hình có độ chính xác cao hơn do các ràng buộc tính toán thấp hơn

**Ví dụ**: "Kết luận chính trong bài báo nghiên cứu dài 50 trang này là gì?"

### Hỏi và đáp trong các tệp lớn (hơn 1000 trang)
**Nguyên tắc**: Xử lý streaming với chỉ mục phân cấp
- Nội dung được truyền theo lô để quản lý bộ nhớ
- Cấu trúc tóm tắt đa cấp (3 cấp phân cấp)
- Tìm kiếm lũy tiến: tóm tắt → các phần → các đoạn chi tiết
- Tối ưu hóa ngữ cảnh với tóm tắt động

**Ví dụ**: "Tìm tất cả các đề cập đến tác động của biến đổi khí hậu trong báo cáo môi trường dài 2000 trang này."

### Hỏi và đáp trên nhiều tệp
**Nguyên tắc**: Xử lý song song với tổng hợp thông tin từ nhiều tài liệu
- Các tài liệu được xử lý đồng thời với chỉ mục hợp nhất
- Ánh xạ mối quan hệ giữa các tài liệu
- Tổng hợp thông tin với xác minh tính nhất quán
- Giải quyết xung đột thông qua trọng số bằng chứng

**Ví dụ**: "So sánh các dự báo kinh tế trên tất cả các báo cáo hàng quý từ năm 2020-2023."

### Tìm kiếm toàn văn bản chính xác
**Nguyên tắc**: Tìm kiếm đa phương pháp với xác thực
- **Khớp chính xác**: Thuật toán Boyer-Moore cho các cụm từ nguyên văn
- **Khớp mờ**: Khoảng cách Levenshtein cho các lỗi chính tả/biến thể
- **Các mẫu Regex**: Khớp mẫu phức tạp
- **Xác minh ngữ nghĩa**: Xác thực kết quả dựa trên ngữ cảnh

**Ví dụ**: "Tìm tất cả các đề cập chính xác về 'mục tiêu phát triển bền vững' và các biến thể của chúng."

### Tổng hợp và đếm
**Nguyên tắc**: Xác thực đa phương pháp với tính điểm tin cậy
- **Nhận dạng thực thể có tên**: Trích xuất thực thể do AI cung cấp
- **Khớp mẫu**: Đếm dựa trên regex với xác thực ngữ cảnh
- **Đếm dựa trên ML**: Hiểu theo ngữ cảnh các đề cập
- **Xác thực chéo**: Các kết quả được đối chiếu bằng cách sử dụng trọng số tin cậy

**Ví dụ**: "Có bao nhiêu con gà được đề cập trong tất cả các tài liệu nông nghiệp?"

**Quy trình**:
1. Trích xuất các thực thể bằng 4 phương pháp khác nhau
2. Xác thực từng đề cập trong ngữ cảnh (tránh các phủ định, giả định)
3. Xác thực chéo các kết quả và tính điểm tin cậy
4. Xử lý các trường hợp không rõ ràng và cung cấp phân tích chi tiết

---

## QDRANT - DOCKER

```bash
# Đầu tiên, tải xuống hình ảnh Qdrant mới nhất từ Dockerhub:
docker pull qdrant/qdrant

# Sau đó, chạy dịch vụ:
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant
```

---

### Cài đặt thư viện

```sh
sudo apt-get update && apt-get install -y \
    build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libsqlite3-dev ffmpeg libsm6 libxext6 libbz2-dev \
    libssl-dev libreadline-dev libffi-dev wget curl \
    python3-venv nano tesseract-ocr libtesseract-dev poppler-utils gfortran libopenblas-dev liblapack-dev && \
    rm -rf /var/lib/apt/lists/*
    
python3.10 -m venv venv
source venv/bin/activate                # venv\Scripts\activate.bat
pip3.10 install -r requirements.txt --use-deprecated=legacy-resolver

pip3.10 install 'uvicorn[standard]'
pip3.10 install --upgrade camelot-py[cv]
pip3.10 install --upgrade tiktoken

cp .env.examples .env

wget https://github.com/tesseract-ocr/tessdata/raw/main/vie.traineddata
sudo mv -v vie.traineddata /usr/share/tesseract-ocr/4.00/tessdata/

ulimit -n 102400

pip3.10 install onnx==1.16.1 onnxruntime==1.19.2
pip3.10 install PyPDF2==2.12.1

python3.10 -m spacy download en_core_web_sm
python3.10 -m spacy download vi_core_news_sm
```

---

### API

```bash
# Chatbot API
python3.10 app.py

# Streamlit UI
streamlit run webui.py --server.enableCORS=false --server.enableXsrfProtection=false
```

---

## DOCKER

### Kéo hình ảnh từ Docker Hub
```bash
docker pull mekongaidnhk/mekongai-template:latest

docker run -d -p 8066:8066 \
  --name mekongai-template \
  -e PORT=1979 \
  -e USER_AGENT="MEKONGAI" \
  -e SERVER_ADDRESS="http://<host>:8066" \
  -e OPENAI_API_BASE_URL="https://api.openai.com/v1" \
  -e OPENAI_API_KEY="<openai-api-key>" \
  -e QDRANT_HOST="<host>" \
  -e QDRANT_PORT="6333" \
  -e QDRANT_SERVER="http://<host>:6333" \
  -e QDRANT_API_KEY="<qdrant-api-key>" \
  mekongaidnhk/mekongai-template:latest
``` 

### hoặc Xây dựng hình ảnh Docker
```bash
# Xây dựng hình ảnh Docker
sudo docker build --no-cache -t mekongaidnhk/mekongai-template:latest .

# Đẩy lên Docker Hub
sudo docker tag mekongaidnhk/mekongai-template mekongaidnhk/mekongai-template:latest
sudo docker push mekongaidnhk/mekongai-template:latest

# Xem nhật ký container
docker logs -f mekongai-template

# Dừng và xóa container
docker stop mekongai-template
docker rm -f mekongai-template

# Xem các tệp trong container
docker exec -it mekongai-template /bin/sh
docker restart mekongai-template
```