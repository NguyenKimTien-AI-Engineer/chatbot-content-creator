import re


def process_txt(file_path):
    """Xử lý file TXT chuẩn: tách theo đoạn trống (\n\n)."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Chia nhỏ content thành các đoạn
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if not paragraphs:
            paragraphs = [content]

        return paragraphs, []
    except Exception as e:
        print(f"Error processing TXT file: {e}")
        return [], []


def process_products_txt(file_path):
    """Xử lý file TXT danh sách sản phẩm: tách mỗi sản phẩm thành một block.

    Định dạng mong đợi cho mỗi sản phẩm:
    "<số thứ tự>. <tên sản phẩm>\nMô tả sản phẩm:\n<mô tả...>\n\n"

    - Nhận diện tiêu đề bằng regex r"^(\d+)\.\s+(.*)$".
    - Nhận diện dòng "Mô tả sản phẩm:" (không phân biệt hoa thường).
    - Gom toàn bộ phần mô tả cho đến dòng trống hoặc tiêu đề kế tiếp.
    - Trả về danh sách chuỗi đã chuẩn hóa cho từng sản phẩm.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = [ln.rstrip('\n') for ln in file.read().splitlines()]

        products = []
        i = 0
        n = len(lines)

        while i < n:
            title_match = re.match(r"^(\d+)\.\s+(.*)$", lines[i].strip())
            if not title_match:
                i += 1
                continue

            index = title_match.group(1)
            title = title_match.group(2).strip()

            # Tìm dòng bắt đầu mô tả
            desc_start = i + 1
            if desc_start < n and "mô tả sản phẩm" in lines[desc_start].strip().lower():
                desc_start += 1

            # Gom mô tả đến khi gặp dòng trống hoặc tiêu đề kế tiếp
            desc_lines = []
            j = desc_start
            while j < n:
                s = lines[j].strip()
                if s == "":
                    break
                if re.match(r"^\d+\.\s+", s):
                    break
                desc_lines.append(s)
                j += 1

            description = " ".join(desc_lines).strip()
            block = f"{index}. {title}\nMô tả sản phẩm:\n{description}".strip()
            products.append(block)

            # Tiếp tục sau khối mô tả (bỏ qua dòng trống nếu có)
            i = j + 1

        return products, []
    except Exception as e:
        print(f"Error processing products TXT file: {e}")
        return [], []