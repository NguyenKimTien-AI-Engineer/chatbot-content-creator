# 1) Base image
FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

# 2) Cài dependencies hệ thống
RUN apt-get update && apt-get install -y \
    build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev \
    libsqlite3-dev ffmpeg libsm6 libxext6 libbz2-dev libssl-dev \
    libreadline-dev libffi-dev wget curl python3.10-venv python3.10-dev \
    nano tesseract-ocr libtesseract-dev poppler-utils gfortran \
    libopenblas-dev liblapack-dev && \
    rm -rf /var/lib/apt/lists/*

# 3) Giới hạn tài nguyên (nếu cần)
RUN echo "* soft nofile 102400" >> /etc/security/limits.conf && \
    echo "* hard nofile 102400" >> /etc/security/limits.conf && \
    echo "fs.file-max = 204800" >> /etc/sysctl.conf && sysctl -p

# 4) Tạo thư mục dữ liệu tĩnh
RUN mkdir -p files/datas/user/CHATBOT_DOCS_V2 files/datas/public/CHATBOT_DOCS_V2

# 5) Thiết lập WORKDIR
WORKDIR /app
RUN mkdir -p /app/logs

# 6) Copy source vào
COPY . .

# 7) Tạo và kích hoạt virtualenv, cài pip + numpy
RUN python3.10 -m venv venv && \
    ./venv/bin/python3.10 -m pip install --upgrade pip && \
    ./venv/bin/python3.10 -m pip install numpy

# 8) Cài đặt code của bạn (install.py) qua venv
RUN ./venv/bin/python3.10 -m pip install -r requirements.txt --use-deprecated=legacy-resolver

# 9) Cài các thư viện còn lại qua venv
RUN ./venv/bin/python3.10 -m pip install \
        "uvicorn[standard]" \
        camelot-py[cv] \
        "unstructured[all-docs]" \
        unstructured_inference \
        opensearch-py \
        langchain_core langchain langchain-qdrant langchain-openai langchain-community \
        pymupdf fastapi aiofiles PyPDF2==2.12.1 boto3 \
        streamlit

# 10) Thiết lập đường dẫn lưu NLTK và download dữ liệu
ENV NLTK_DATA=/app/nltk_data
RUN mkdir -p /app/nltk_data && \
    ./venv/bin/python3.10 -m nltk.downloader all -d /app/nltk_data

# 11) Expose port và khởi động
EXPOSE 8066
CMD ["./venv/bin/python3.10", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "1953"]
