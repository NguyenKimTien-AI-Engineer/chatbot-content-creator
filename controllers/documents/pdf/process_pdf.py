import camelot
import fitz
import base64
import pandas as pd
from unstructured.partition.pdf import partition_pdf
import pdfplumber
import pytesseract
from PIL import Image
import io
import cv2
import numpy as np
from pdf2image import convert_from_path
import tempfile
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def detect_pdf_type(file_path):
    """
    Phân loại loại PDF để chọn phương pháp xử lý phù hợp
    Returns:
    - 'text': PDF có text có thể trích xuất
    - 'table': PDF có nhiều bảng
    - 'complex': PDF layout phức tạp
    - 'scanned': PDF được scan (cần OCR)
    """
    try:
        with fitz.open(file_path) as doc:
            total_chars = 0
            total_images = 0
            total_tables = 0
            
            # Kiểm tra 3 trang đầu để phân loại
            pages_to_check = min(3, doc.page_count)
            
            for page_num in range(pages_to_check):
                page = doc.load_page(page_num)
                
                # Đếm ký tự text
                text = page.get_text()
                total_chars += len(text.strip())
                
                # Đếm hình ảnh
                image_list = page.get_images()
                total_images += len(image_list)
                
                # Kiểm tra có bảng không bằng cách phát hiện đường kẻ
                drawings = page.get_drawings()
                table_like_drawings = sum(1 for d in drawings if 'rect' in str(d).lower())
                total_tables += table_like_drawings
            
            avg_chars_per_page = total_chars / pages_to_check
            avg_images_per_page = total_images / pages_to_check
            avg_tables_per_page = total_tables / pages_to_check
            
            # Logic phân loại
            if avg_chars_per_page < 100 and avg_images_per_page > 0.5:
                return 'scanned'
            elif avg_tables_per_page > 3 or total_tables > 5:
                return 'table'
            elif avg_chars_per_page > 500:
                return 'text'
            else:
                return 'complex'
                
    except Exception as e:
        logger.warning(f"Cannot detect PDF type: {e}, defaulting to 'complex'")
        return 'complex'

def extract_text_pdf(file_path, language):
    """Trích xuất PDF text thuần túy"""
    try:
        raw_data_elements = partition_pdf(filename=file_path, languages=[language])
        return raw_data_elements
    except Exception as e:
        logger.error(f"Text extraction failed: {e}")
        return []

def extract_table_pdf(file_path):
    """Trích xuất PDF có nhiều bảng"""
    results = []
    
    # Thử pdfplumber trước (ổn định hơn)
    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_results = []
                
                # Trích xuất bảng
                tables = page.extract_tables()
                if tables:
                    for table_idx, table in enumerate(tables):
                        if table and len(table) > 0:
                            # Tạo DataFrame từ bảng
                            df = pd.DataFrame(table[1:], columns=table[0] if table[0] else None)
                            page_results.append({
                                "page": page_num,
                                "data": df,
                                "type": "table",
                                "table_index": table_idx
                            })
                
                # Trích xuất text còn lại (không nằm trong bảng)
                try:
                    # Lấy toàn bộ text
                    full_text = page.extract_text()
                    if full_text and full_text.strip():
                        # Tạo object giống unstructured format
                        class TextElement:
                            def __init__(self, text, page_num):
                                self.text = text
                                self.metadata = type('obj', (object,), {'page_number': page_num})()
                        
                        page_results.append(TextElement(full_text.strip(), page_num))
                except Exception as text_error:
                    logger.warning(f"Text extraction failed for page {page_num}: {text_error}")
                
                results.extend(page_results)
        
        return results
    except Exception as e:
        logger.error(f"PDFPlumber extraction failed: {e}")
    
    # Fallback: Thử Camelot nếu pdfplumber thất bại
    try:
        # Sử dụng pdfplumber thay vì camelot để tránh lỗi PyPDF2
        logger.info("Using fallback text extraction method")
        return extract_text_pdf(file_path, 'en')  # fallback
    except Exception as e:
        logger.error(f"Fallback extraction failed: {e}")
        return []

def extract_complex_pdf(file_path, language):
    """Trích xuất PDF layout phức tạp"""
    try:
        # Sử dụng unstructured với nhiều tùy chọn
        raw_data_elements = partition_pdf(
            filename=file_path, 
            languages=[language],
            strategy="hi_res",  # Độ phân giải cao
            infer_table_structure=True,  # Phát hiện bảng
            extract_images=True  # Trích xuất hình ảnh
        )
        return raw_data_elements
    except Exception as e:
        logger.error(f"Complex PDF extraction failed: {e}")
        # Fallback to basic extraction
        try:
            return partition_pdf(filename=file_path, languages=[language])
        except Exception as fallback_error:
            logger.error(f"Fallback complex extraction failed: {fallback_error}")
            return []

def preprocess_image_for_ocr(image):
    """Tiền xử lý ảnh để cải thiện OCR"""
    try:
        # Chuyển PIL Image thành numpy array
        img_array = np.array(image)
        
        # Chuyển sang grayscale
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Áp dụng threshold để tăng độ tương phản
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Khử noise
        denoised = cv2.medianBlur(thresh, 3)
        
        # Chuyển lại thành PIL Image
        return Image.fromarray(denoised)
    except Exception as e:
        logger.warning(f"Image preprocessing failed: {e}")
        return image

def extract_scanned_pdf(file_path, language):
    """Trích xuất PDF được scan (OCR)"""
    results = []
    
    try:
        # Chuyển PDF thành images
        with tempfile.TemporaryDirectory() as temp_dir:
            images = convert_from_path(file_path, dpi=300, output_folder=temp_dir)
            
            def process_page_ocr(page_data):
                page_num, image = page_data
                try:
                    # Tiền xử lý ảnh
                    processed_image = preprocess_image_for_ocr(image)
                    
                    # OCR với Tesseract
                    lang_map = {
                        'vi': 'vie',
                        'en': 'eng',
                        'zh': 'chi_sim'
                    }
                    tesseract_lang = lang_map.get(language, 'eng')
                    
                    # Trích xuất text
                    text = pytesseract.image_to_string(
                        processed_image, 
                        lang=tesseract_lang,
                        config='--psm 6'  # Assume uniform block of text
                    )
                    
                    if text.strip():
                        # Tạo object giống unstructured format
                        class OCRElement:
                            def __init__(self, text, page_num):
                                self.text = text
                                self.metadata = type('obj', (object,), {'page_number': page_num})()
                        
                        return OCRElement(text.strip(), page_num)
                    
                    return None
                except Exception as e:
                    logger.error(f"OCR failed for page {page_num}: {e}")
                    return None
            
            # Xử lý song song các trang
            with ThreadPoolExecutor(max_workers=4) as executor:
                page_data = [(i + 1, img) for i, img in enumerate(images)]
                results = list(executor.map(process_page_ocr, page_data))
        
        return [r for r in results if r is not None]
        
    except Exception as e:
        logger.error(f"Scanned PDF extraction failed: {e}")
        return []

def process_pdf(folder_path, file_path, language, export_base64=False):
    try:
        if export_base64:
            pdf_files, path_images, page_image_base64_list = split_pdf_files_in_folder(folder_path, file_path)
        else:
            # Chỉ lấy số trang để tạo mảng placeholder
            with fitz.open(file_path) as doc:
                total_pages = doc.page_count
            pdf_files, path_images, page_image_base64_list = [], [], [""] * total_pages
    except Exception as e:
        logger.error(f"PDF splitting failed: {e}")
        pdf_files, path_images, page_image_base64_list = [], [], []

    raw_elements = []
    
    try:
        pdf_type = detect_pdf_type(file_path)
        logger.info(f"Detected PDF type: {pdf_type}")
        
        # Xử lý theo loại PDF
        if pdf_type == 'scanned':
            raw_data_elements = extract_scanned_pdf(file_path, language)
        elif pdf_type == 'table':
            raw_data_elements = extract_table_pdf(file_path)
        elif pdf_type == 'complex':
            raw_data_elements = extract_complex_pdf(file_path, language)
        else:  # text
            raw_data_elements = extract_text_pdf(file_path, language)
        
        # Xử lý kết quả theo format cũ
        total_pages = len(page_image_base64_list) if page_image_base64_list else 1
        raw_elements = [[] for _ in range(total_pages)]
        
        for element in raw_data_elements:
            try:
                # Xử lý element theo loại
                if isinstance(element, dict):
                    # Đây là kết quả từ table extraction
                    page_num = element.get("page", 1)
                    if 1 <= page_num <= total_pages:
                        raw_elements[page_num - 1].append(element)
                    else:
                        logger.warning(f"Invalid page number: {page_num}")
                elif hasattr(element, 'metadata') and hasattr(element.metadata, 'page_number'):
                    # Đây là element từ unstructured hoặc OCR
                    page_number = element.metadata.page_number
                    if page_number is not None and 1 <= page_number <= total_pages:
                        raw_elements[page_number - 1].append(element)
                    else:
                        logger.warning(f"Element with invalid page number: {page_number}")
                        # Đặt vào trang đầu như fallback
                        if total_pages > 0:
                            raw_elements[0].append(element)
                else:
                    # Nếu không có page info, đặt vào trang đầu
                    if total_pages > 0:
                        raw_elements[0].append(element)
            except Exception as element_error:
                logger.warning(f"Error processing element: {element_error}")
                continue
        
        # Đảm bảo page_image_base64_list có cùng size với raw_elements
        if not export_base64 and len(page_image_base64_list) != len(raw_elements):
            page_image_base64_list = [""] * len(raw_elements)
        
        # Log kết quả
        for i, page in enumerate(raw_elements):
            logger.info(f"Page {i + 1} has {len(page)} elements.")
            
    except Exception as e:
        logger.error(f"PDF processing failed: {e}")
        # Fallback về phương pháp cũ
        try:
            raw_data_elements = partition_pdf(filename=file_path, languages=[language])
            total_pages = len(page_image_base64_list) if page_image_base64_list else 1
            raw_elements = [[] for _ in range(total_pages)]
            
            for element in raw_data_elements:
                try:
                    if hasattr(element, 'metadata') and hasattr(element.metadata, 'page_number'):
                        page_number = element.metadata.page_number
                        if page_number is not None and 1 <= page_number <= total_pages:
                            raw_elements[page_number - 1].append(element)
                        else:
                            raw_elements[0].append(element)
                    else:
                        raw_elements[0].append(element)
                except Exception:
                    continue
                
            # Đảm bảo page_image_base64_list có cùng size với raw_elements
            if not export_base64:
                page_image_base64_list = [""] * len(raw_elements)
                
        except Exception as fallback_error:
            logger.error(f"Fallback processing failed: {fallback_error}")
            raw_elements = []

    # Cleanup - sửa lỗi file path
    try:
        # Chuyển string thành Path object nếu cần
        if isinstance(file_path, str):
            file_path = Path(file_path)
        remove_file(file_path)
    except Exception as e:
        logger.warning(f"File cleanup failed: {e}")

    return raw_elements, page_image_base64_list

def remove_file(file_path_rm):
    try:
        # Đảm bảo file_path_rm là Path object
        if isinstance(file_path_rm, str):
            file_path_rm = Path(file_path_rm)
            
        if file_path_rm.exists():
            file_path_rm.unlink()
            print("File removed successfully.")
    except PermissionError as e:
        print("File remove error: ", e)
        pass
    except Exception as e:
        print(f"File remove error: {e}")
        pass

def split_pdf_files_in_folder(folder_path, file_path):
    pdf_files = []
    path_images = []

    page_image_base64_list = pdf_to_base64_array(file_path)

    # for filename in os.listdir(folder_path):
    #     if filename.endswith(".pdf"):
    #         file_path = folder_path / filename
    #         with open(file_path, "rb") as pdf_file:
    #             pdf = PdfReader(pdf_file)
    #
    #             output_dir = folder_path / "splits" / file_path.stem
    #             output_dir.mkdir(parents=True, exist_ok=True)
    #
    #             for i in range(len(pdf.pages)):
    #                 output = PdfWriter()
    #                 output.add_page(pdf.pages[i])
    #
    #                 path_image = (
    #                         folder_path
    #                         / "splits"
    #                         / file_path.stem
    #                         / f"{file_path.stem}-page-{i + 1}"
    #                 )
    #                 output_file_path = output_dir / f"{file_path.stem}-page-{i + 1}.pdf"
    #                 with open(output_file_path, "wb") as outputStream:
    #                     output.write(outputStream)
    #
    #                 pdf_files.append(str(output_file_path))
    #                 path_images.append(str(path_image))
    #
    #                 # Chuyển đổi mỗi trang PDF thành ảnh và lưu vào base64 (chỉ giữ 1 ảnh duy nhất)
    #                 images = convert_from_path(str(output_file_path), first_page=1, last_page=1)
    #                 if images:
    #                     buffered = BytesIO()
    #                     images[0].save(buffered, format="JPEG")
    #                     img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    #
    #                     # Lưu base64 của trang vào mảng theo đúng thứ tự
    #                     page_image_base64_list.append(img_base64)
    #
    #             print(f"Saved {filename} to {output_dir}")

    # threading.Thread(target=remove_file, args=(file_path,)).start()

    return pdf_files, path_images, page_image_base64_list


def pdf_to_base64_array(pdf_path):
    """Chuyển mỗi trang của PDF thành một chuỗi Base64 và lưu vào mảng"""
    base64_pages = []  # Mảng chứa Base64 của từng trang

    # Mở file PDF
    with fitz.open(pdf_path) as pdf_document:
        # Duyệt qua từng trang của PDF
        for page_num in range(pdf_document.page_count):
            # Tải trang hiện tại
            page = pdf_document.load_page(page_num)

            # Kiểm tra kích thước gốc của trang
            width, height = page.rect.width, page.rect.height

            # Tính tỉ lệ zoom để đảm bảo chiều rộng ít nhất là 1200px
            zoom_x = 1200 / width
            zoom_y = zoom_x  # Giữ tỉ lệ đồng nhất để không làm biến dạng ảnh
            matrix = fitz.Matrix(zoom_x, zoom_y)

            # Chuyển trang thành ảnh (PNG) với độ phân giải cao hơn
            pix = page.get_pixmap(matrix=matrix)
            page_content = pix.tobytes()  # Lấy binary từ trang

            # Mã hóa binary của trang thành Base64
            encoded_string = base64.b64encode(page_content).decode('utf-8')
            base64_pages.append(encoded_string)  # Thêm vào mảng

    return base64_pages
