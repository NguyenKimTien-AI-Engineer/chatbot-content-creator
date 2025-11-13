import re
from collections import OrderedDict


def extract_reference_document_numbers(text):
    try:
        text = text.lower().strip()

        numbers_ref = []

        fallback_pattern = r"📑.*?([\d,\s]+)"
        fallback_match = re.search(fallback_pattern, text, re.IGNORECASE)
        if fallback_match:
            numbers_ref = [int(num) for num in re.findall(r"\d+", fallback_match.group(1))]

        # **Tìm kiếm các số trong "[number]"**
        pattern_brackets = r"\[(\d+)\]"
        numbers_brackets = [int(num) for num in re.findall(pattern_brackets, text)]

        # **Kết hợp và loại bỏ trùng lặp, giữ thứ tự xuất hiện**
        seen = OrderedDict()
        # Thêm các số từ "📑" trước
        for num in numbers_ref:
            seen[num] = None
        # Thêm các số từ "[number]" sau
        for num in numbers_brackets:
            seen[num] = None

        # Trả về danh sách các số không trùng lặp theo thứ tự xuất hiện
        return list(seen.keys()) if seen else None

    except Exception as e:
        print(f"⚠️ Lỗi xảy ra ở extract_reference_document_numbers: {e}")
        return None


def filter_reference_from_page(references, pages):
    try:
        final_references = []

        for page in pages:
            final_references.append(references[int(page)])

        return final_references

    except Exception as e:
        print(f"⚠️ Lỗi xảy ra ở filter_reference_from_page: {e}")
        return references

