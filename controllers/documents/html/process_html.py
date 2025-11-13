from bs4 import BeautifulSoup
import re

def process_html(file_path):
    """Xử lý file HTML"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Loại bỏ script và style tags
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Lấy text và chia thành paragraphs
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text_content = ' '.join(chunk for chunk in chunks if chunk)
        
        # Chia thành các đoạn
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text_content) if p.strip()]
        if not paragraphs:
            paragraphs = [text_content]
            
        return paragraphs, []
    except Exception as e:
        print(f"Error processing HTML file: {e}")
        return [], []