def process_txt(file_path):
    """Xử lý file TXT"""
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