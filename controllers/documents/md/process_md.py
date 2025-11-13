import re

def process_md(file_path):
    """Xử lý file Markdown"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Chia content thành sections dựa trên headers
        sections = re.split(r'\n(?=#{1,6}\s)', content)
        sections = [section.strip() for section in sections if section.strip()]
        
        if not sections:
            # Nếu không có header, chia theo paragraph
            sections = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        if not sections:
            sections = [content]
            
        return sections, []
    except Exception as e:
        print(f"Error processing MD file: {e}")
        return [], []