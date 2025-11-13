import pandas as pd

def process_csv(file_path):
    """Xử lý file CSV"""
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        
        # Chuyển đổi DataFrame thành text có cấu trúc
        content_parts = []
        
        # Thêm header
        headers = ', '.join(df.columns.tolist())
        content_parts.append(f"Headers: {headers}")
        
        # Thêm từng row
        for idx, row in df.iterrows():
            row_text = ', '.join([f"{col}: {val}" for col, val in row.items()])
            content_parts.append(f"Row {idx + 1}: {row_text}")
        
        return content_parts, []
    except Exception as e:
        print(f"Error processing CSV file: {e}")
        return [], []