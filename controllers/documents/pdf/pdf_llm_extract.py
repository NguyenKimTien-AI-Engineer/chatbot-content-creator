import pytesseract
import pdf2image
import pandas as pd
import numpy as np
import base64
from io import BytesIO
import json
import camelot
import cv2
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import time

from configs import environment

class TableRow(BaseModel):
    cells: List[str] = Field(description="List of cell values in the row")

class Table(BaseModel):
    table_number: int = Field(description="Sequential number of the table on the page")
    title: Optional[str] = Field(description="Title or caption of the table if any", default="")
    headers: List[str] = Field(description="Column headers of the table")
    rows: List[List[str]] = Field(description="Rows of data, each row is a list of cell values")

class PageTables(BaseModel):
    tables: List[Table] = Field(description="List of all tables found on the page")

class DocumentContent(BaseModel):
    page_number: int = Field(description="Page number")
    content_blocks: List[dict] = Field(description="All content blocks in order with type and content")

class ContentBlock(BaseModel):
    type: str = Field(description="Type of content: 'text', 'table', 'heading', 'list', 'image_caption'")
    content: dict = Field(description="Content data specific to the type")
    position: int = Field(description="Sequential position on the page")

def nomal_file_name_to_md(file_name):
    """
    Normalize file name to a valid markdown file name.
    - Convert to lowercase
    - Remove Vietnamese diacritics
    - Replace spaces with hyphens
    - Add .md extension
    """
    # Remove the .pdf extension if it exists
    if file_name.lower().endswith('.pdf'):
        file_name = file_name[:-4]
    
    # Convert to lowercase and remove Vietnamese diacritics
    nfkd_form = unicodedata.normalize('NFKD', file_name)
    ascii_name = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    cleaned_name = ascii_name.lower().replace("đ", "d")  # Handle 'đ' specifically
    
    # Replace spaces with hyphens (or underscores if preferred), and add the new extension
    final_name = " ".join(cleaned_name.split()) + ".md"
    
    return final_name


def resize_image_for_llm(image, max_size=1024):
    """Resize image to optimize for LLM processing while maintaining quality"""
    width, height = image.size
    
    # Calculate scaling factor
    if max(width, height) > max_size:
        scale_factor = max_size / max(width, height)
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        
        # Use LANCZOS for high-quality resizing
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        print(f"Resized from {width}x{height} to {new_width}x{new_height}")
        return resized_image
    
    return image

def extract_complete_document_with_llm(pdf_path, llm_model, pages='all', max_image_size=1024):
    """Extract complete document content including text and tables with exact structure preservation"""
    
    if pages == 'all':
        images = pdf2image.convert_from_path(pdf_path, dpi=200)
    else:
        images = pdf2image.convert_from_path(pdf_path, first_page=pages, last_page=pages, dpi=200)
    
    all_content = []
    
    # Enhanced prompt for complete document extraction
    extraction_prompt = """
    Bạn là chuyên gia phân tích tài liệu PDF hàng đầu. Hãy trích xuất TOÀN BỘ nội dung từ hình ảnh này theo đúng thứ tự và cấu trúc gốc.

    NHIỆM VỤ CHÍNH:
    1. QUÉT TOÀN BỘ trang từ trên xuống dưới, trái sang phải
    2. NHẬN DIỆN và PHÂN LOẠI tất cả loại content: text, headings, tables, lists, captions
    3. GIỮ NGUYÊN 100% thứ tự xuất hiện của content
    4. TRÍCH XUẤT HOÀN TOÀN mọi thông tin (không bỏ sót)
    5. BẢO TOÀN định dạng, cấu trúc, và mối quan hệ giữa các phần

    LOẠI CONTENT CẦN NHẬN DIỆN:
    - "heading": Tiêu đề, đề mục (các cấp khác nhau)
    - "text": Đoạn văn bản thường
    - "table": Bảng biểu (có cấu trúc hàng-cột)
    - "list": Danh sách có bullet hoặc số thứ tự
    - "image_caption": Chú thích hình ảnh, bảng

    QUY TRÌNH PHÂN TÍCH:
    1. Quét từ đầu trang đến cuối trang
    2. Xác định vị trí và loại của từng content block
    3. Trích xuất nội dung chi tiết cho từng block
    4. Ghi nhận thứ tự chính xác (position)
    5. Đặc biệt chú ý đến tables: headers, rows, merged cells

    YÊU CẦU ĐẦU RA JSON:
    (
        "page_number": 1,
        "content_blocks": [
            (
                "type": "heading",
                "content": ("text": "Tiêu đề chính", "level": 1),
                "position": 1
            ),
            (
                "type": "text", 
                "content": ("text": "Nội dung đoạn văn..."),
                "position": 2
            ),
            (
                "type": "table",
                "content": (
                    "title": "Tên bảng nếu có",
                    "headers": ["Cột 1", "Cột 2"],
                    "rows": [["Dữ liệu 1", "Dữ liệu 2"]]
                ),
                "position": 3
            )
        ]
    )

    LƯU Ý QUAN TRỌNG:
    - Giữ nguyên chính tả, dấu câu, số liệu
    - Không thay đổi thứ tự content
    - Với bảng: trích xuất đầy đủ headers và tất cả rows
    - Với text: giữ nguyên line breaks và formatting
    - Phân biệt rõ các cấp heading
    - Nhận diện chính xác lists và numbering
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", extraction_prompt),
        ("human", [
            {"type": "text", "text": "Phân tích toàn bộ nội dung trang này theo đúng thứ tự và cấu trúc:"},
            {"type": "image_url", "image_url": {"url": "{image_url}"}},
        ]),
    ])
    
    parser = JsonOutputParser(pydantic_object=DocumentContent)
    chain = prompt | llm_model | parser
    
    for page_num, image in enumerate(images, 1):
        start_time = time.time()
        print(f"🔍 Extracting complete content from page {page_num}...")
        
        try:
            optimized_image = resize_image_for_llm(image, max_image_size)
            
            buffered = BytesIO()
            if optimized_image.mode == 'RGBA':
                optimized_image = optimized_image.convert('RGB')
            
            optimized_image.save(buffered, format="JPEG", quality=85, optimize=True)
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            image_url = f"data:image/jpeg;base64,{img_base64}"
            
            result = chain.invoke({"image_url": image_url})
            
            if hasattr(result, 'content_blocks'):
                page_content = {
                    'page': page_num,
                    'content_blocks': result.content_blocks
                }
                all_content.append(page_content)
                print(f"  ✅ Found {len(result.content_blocks)} content blocks")
                
            elif isinstance(result, dict) and 'content_blocks' in result:
                page_content = {
                    'page': page_num,
                    'content_blocks': result['content_blocks']
                }
                all_content.append(page_content)
                print(f"  ✅ Found {len(result['content_blocks'])} content blocks")
                
            process_time = time.time() - start_time
            print(f"  ⏱️ Page {page_num} processed in {process_time:.2f}s")
                    
        except Exception as e:
            print(f"❌ Error processing page {page_num}: {e}")
    
    return all_content

def export_complete_document_to_markdown(content_data, output_file="complete_document.md"):
    """Export complete document content to markdown preserving structure"""
    
    markdown_content = []
    
    total_blocks = 0
    total_tables = 0
    
    for page_data in content_data:
        page_num = page_data['page']
        content_blocks = page_data['content_blocks']
        
        markdown_content.append(f"\n## 📄 Page {page_num}\n")
        
        # Handle both list and dict formats for content_blocks
        if isinstance(content_blocks, list):
            # Sort blocks by position to maintain order
            sorted_blocks = []
            for block in content_blocks:
                if isinstance(block, dict):
                    sorted_blocks.append(block)
                else:
                    # Convert to dict format if needed
                    print(f"⚠️ Unexpected block format: {type(block)}, converting...")
                    continue
            
            # Sort by position
            sorted_blocks = sorted(sorted_blocks, key=lambda x: x.get('position', 0))
        else:
            print(f"⚠️ Unexpected content_blocks format: {type(content_blocks)}")
            continue
        
        for block in sorted_blocks:
            try:
                content_type = block.get('type', 'unknown')
                content_data_block = block.get('content', {})
                
                if content_type == 'heading':
                    level = content_data_block.get('level', 1)
                    text = content_data_block.get('text', '')
                    heading_marker = '#' * (level + 2)  # +2 because we start with ## for page
                    markdown_content.append(f"{heading_marker} {text}\n")
                    
                elif content_type == 'text':
                    text = content_data_block.get('text', '')
                    markdown_content.append(f"{text}\n")
                    
                elif content_type == 'table':
                    total_tables += 1
                    title = content_data_block.get('title', '')
                    headers = content_data_block.get('headers', [])
                    rows = content_data_block.get('rows', [])
                    
                    if title:
                        markdown_content.append(f"**📋 {title}**\n")
                    
                    if headers and rows:
                        # Create markdown table
                        header_row = "| " + " | ".join([str(h) for h in headers]) + " |"
                        separator = "|" + "|".join([" --- " for _ in headers]) + "|"
                        markdown_content.append(header_row)
                        markdown_content.append(separator)
                        
                        for row in rows:
                            formatted_row = []
                            for cell in row:
                                cell_str = str(cell) if cell is not None else ""
                                cell_str = cell_str.replace("|", "\\|")
                                formatted_row.append(cell_str)
                            
                            row_text = "| " + " | ".join(formatted_row) + " |"
                            markdown_content.append(row_text)
                        
                        markdown_content.append("")  # Empty line after table
                    
                elif content_type == 'list':
                    # Handle both formats: dict with 'items' key or direct list
                    if isinstance(content_data_block, dict):
                        # Standard format: {'items': [...], 'list_type': '...'}
                        items = content_data_block.get('items', [])
                        list_type = content_data_block.get('list_type', 'bullet')
                    elif isinstance(content_data_block, list):
                        # Direct list format: ['item1', 'item2', ...]
                        items = content_data_block
                        list_type = 'bullet'  # Default to bullet
                    else:
                        print(f"⚠️ Unexpected list content format: {type(content_data_block)}")
                        items = []
                        list_type = 'bullet'
                    
                    for i, item in enumerate(items):
                        if list_type == 'numbered':
                            markdown_content.append(f"{i+1}. {item}")
                        else:
                            markdown_content.append(f"- {item}")
                    markdown_content.append("")  # Empty line after list
                    
                elif content_type == 'image_caption':
                    if isinstance(content_data_block, dict):
                        text = content_data_block.get('text', '')
                    else:
                        text = str(content_data_block)
                    markdown_content.append(f"*{text}*\n")
                
                total_blocks += 1
                
            except Exception as e:
                print(f"⚠️ Error processing block: {e}")
                print(f"Block data: {block}")
                print(f"Content type: {content_type}")
                print(f"Content data type: {type(content_data_block)}")
                continue
    
    # Add summary
    markdown_content.append(f"\n\n")
    markdown_content.append(f"**Document Summary:**")
    markdown_content.append(f"- Total pages: {len(content_data)}")
    markdown_content.append(f"- Total content blocks: {total_blocks}")
    markdown_content.append(f"- Total tables: {total_tables}")
    
    # Write to file
    final_content = "\n".join(markdown_content)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"📄 Complete document saved to: {output_file}")
    return final_content

def complete_document_extraction(pdf_path, llm_model=environment.llm_mini, max_image_size=2048):
    """Main function for complete document extraction"""
    
    if not llm_model:
        raise ValueError("LLM model is required for complete document extraction")
    
    print("🚀 Starting complete document extraction...")
    start_time = time.time()
    
    try:
        document_content = extract_complete_document_with_llm(pdf_path, llm_model, max_image_size=max_image_size)
        
        total_time = time.time() - start_time
        print(f"✅ Complete extraction finished in {total_time:.2f}s")
        
        if document_content:
            markdown_content = export_complete_document_to_markdown(document_content, output_file=nomal_file_name_to_md(pdf_path))
            return markdown_content
        else:
            print("⚠️ No content extracted")
            return ""
        
    except Exception as e:
        print(f"❌ Document extraction failed: {e}")
        # Print more detailed error info for debugging
        import traceback
        print("Detailed error:")
        traceback.print_exc()
        return ""

# if __name__ == "__main__":
#     pdf_file_path = 'ketoandoanhnghiep.pdf'
    
#     # Run complete extraction
#     document_content = complete_document_extraction(pdf_file_path)
#     print(document_content)
