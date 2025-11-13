import os
import subprocess
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

# CSS tách riêng
CSS_STYLE = (
    "<style>"
    "body { font-family: Arial, sans-serif; background-color: #f8f8f8; margin: 0; padding: 20px; }"
    "p { line-height: 1.6; text-align: justify; }"
    ".docx-table { border-collapse: collapse; width: 100%; margin-bottom: 1em; }"
    ".docx-table th, .docx-table td { border: 1px solid #ccc; padding: 8px; text-align: left; }"
    ".docx-table th { background-color: #f8f8f8; font-weight: bold; }"
    ".docx-table tr:nth-child(even) { background-color: #f2f2f2; }"
    ".docx-table tr:hover { background-color: #e0e0e0; }"
    "</style>"
)

def paragraph_to_html(paragraph):
    # Giữ nguyên logic của bạn để render <p>, <h4>,... + bold/italic/underline
    style = paragraph.style.name.lower()
    if "heading 1" in style: tag = "h4"
    elif "heading 2" in style: tag = "h5"
    elif "heading 3" in style: tag = "h6"
    else: tag = "p"

    # căn lề
    align = paragraph.alignment
    align_style = ""
    if align == WD_ALIGN_PARAGRAPH.CENTER:  align_style = "text-align: center;"
    elif align == WD_ALIGN_PARAGRAPH.RIGHT:  align_style = "text-align: right;"
    elif align == WD_ALIGN_PARAGRAPH.JUSTIFY:align_style = "text-align: justify;"

    open_tag  = f"<{tag} style='{align_style}'>" if align_style else f"<{tag}>"
    html = open_tag
    for run in paragraph.runs:
        text = (run.text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))
        if not text:
            continue
        # detect page-break trong run
        brs = run._r.findall('.//w:br',
            namespaces={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})
        # apply định dạng
        if run.bold:     text = f"<strong>{text}</strong>"
        if run.italic:   text = f"<em>{text}</em>"
        if run.underline:text = f"<u>{text}</u>"

        # nếu có page-break, append trước rồi đánh dấu flush
        if any(br.get(qn('w:type'))=='page' for br in brs):
            html += text
            html += f"</{tag}>"
            # trả về 2 phần: nội dung trước break, và tín hiệu flush
            return html, True

        html += text

    html += f"</{tag}>"
    return html, False


def table_to_html(table):
    html = "<table class='docx-table'>\n"
    for row in table.rows:
        html += "<tr>\n"
        for cell in row.cells:
            cell_html = ""
            for p in cell.paragraphs:
                part, _ = paragraph_to_html(p)
                cell_html += part
            html += f"<td>{cell_html}</td>\n"
        html += "</tr>\n"
    html += "</table>\n"
    return html


def iter_block_items(parent):
    parent_elm = parent.element.body
    for child in parent_elm.iterchildren():
        if child.tag.endswith('}p'):
            yield Paragraph(child, parent)
        elif child.tag.endswith('}tbl'):
            yield Table(child, parent)


def docx_to_simple_html_pages(docx_path):
    doc = Document(docx_path)
    raw_elements = []
    current_html = CSS_STYLE + "<body>"

    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            p_html, is_break = paragraph_to_html(block)
            current_html += p_html
            if is_break:
                # gặp break ⇒ kết thúc trang cũ
                current_html += "</body>"
                raw_elements.append(current_html)

                # mở trang mới
                current_html = CSS_STYLE + "<body>"
        else:  # Table
            current_html += table_to_html(block)

    # phần còn lại (nếu có)
    if current_html.strip() != CSS_STYLE + "<body>":
        current_html += "</body>"
        raw_elements.append(current_html)

    # tạo danh sách base64 image rỗng
    page_image_base64_list = [''] * len(raw_elements)
    return raw_elements, page_image_base64_list


def convert_doc_to_docx(doc_path, output_dir=None):
    if output_dir is None:
        output_dir = os.path.dirname(doc_path)
    try:
        subprocess.check_call([
            'soffice','--headless','--convert-to','docx',
            '--outdir', output_dir, doc_path
        ])
        base = os.path.splitext(os.path.basename(doc_path))[0]
        return os.path.join(output_dir, base + ".docx")
    except Exception as e:
        print(f"Lỗi chuyển DOC sang DOCX: {e}")
        return None


def process_docx(file_path):
    ext = file_path.lower().split('.')[-1]
    if ext == 'doc':
        docx = convert_doc_to_docx(file_path)
        if not docx:
            return [], []
        return docx_to_simple_html_pages(docx)

    if ext == 'docx':
        return docx_to_simple_html_pages(file_path)

    # không phải DOC/DOCX
    return [], []
