from unstructured.partition.pdf import partition_pdf
import time
from transformers import logging

from configs import constant

logging.set_verbosity_error()


def load_documents(file_path: str):
    raw_elements = partition_pdf(filename=file_path, languages=["vie"], strategy="auto", chunking_strategy="basic")

    return raw_elements


def load_documents_custom(file_path: str, chunk_size=5120, max_chunk_size=10240, chunk_overlap=0,
                          table=False, images=None, path_image="", languages="vie+eng"):
    raw_elements = partition_pdf(filename=file_path,
                                 extract_image_block_types=images,
                                 infer_table_structure=table,
                                 form_extraction_skip_tables=False,
                                 languages=[languages],
                                 strategy="auto",
                                 hi_res_model_name="yolox",
                                 chunking_strategy="by_title",
                                 partitioning_strategies="auto",
                                 max_characters=max_chunk_size,
                                 new_after_n_chars=max_chunk_size,
                                 combine_text_under_n_chars=chunk_size,
                                 multipage_sections=True,
                                 overlap=chunk_overlap,
                                 extract_image_block_output_dir=path_image
                                 )

    return raw_elements



# Test
# from collections import OrderedDict
#
# class OrderedSet:
#     def __init__(self, iterable):
#         self.items = list(OrderedDict.fromkeys(iterable))
#
#     def __repr__(self):
#         return "{" + ", ".join(map(str, self.items)) + "}"
#
#
# # Đọc dữ liệu từ file đầu vào
# raw_data_elements = load_documents("../../files/tests/5.10. LUAT CANH TRANH.pdf")
#
# # Tìm số trang tối đa từ metadata
# total_pages = max(
#     [element.metadata.page_number for element in raw_data_elements if
#      element.metadata.page_number is not None],
#     default=0,
# )
#
# # Khởi tạo raw_elements với danh sách rỗng cho tất cả các trang trước
# raw_elements = [[] for _ in range(total_pages)]
#
# # Duyệt qua tất cả phần tử và phân bổ vào đúng trang trong raw_elements
# for element in raw_data_elements:
#     # Kiểm tra và lấy số trang của phần tử
#     page_number = element.metadata.page_number
#
#     if page_number is not None:
#         # Trừ 1 vì index trong Python bắt đầu từ 0
#         raw_elements[page_number - 1].append(element)
#     else:
#         print(f"| WARNING: Element without page number detected: {element}")
#
# # Log thông tin từng trang đã thêm
# for i, page in enumerate(raw_elements):
#     print(f"| INFO: Page {i + 1} has {len(page)} elements.")
#
#     content_string = ""
#     content_chunks = []
#
#     for element in page:
#         if element.text.strip() == "" or element.text.strip() == "Formatted: Font: Times New Roman, 13 pt":
#             continue
#         content_chunks.append(element.text)
#         content_string += element.text + "\n"
#
#     print(f"| INFO: Content string: {content_string}")


# # Tạo file để lưu kết quả
# output_file_path = "../../files/tests/law_2.txt"
#
# # Mở file ở chế độ ghi ('w'), nếu file không tồn tại sẽ tạo mới
# with open(output_file_path, "w", encoding="utf-8") as f:
#     for element in raw_data_elements:
#         print("=====================================================")
#         print(element.text)
#         print(element.metadata.page_number)
#
#         f.write(element.text)
#         f.write("\n")
#
# print(f"Đã lưu kết quả vào file: {output_file_path}")
