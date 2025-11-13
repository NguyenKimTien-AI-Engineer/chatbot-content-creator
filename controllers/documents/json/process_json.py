import json

def process_json(file_path):
    """Xử lý file JSON"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        def flatten_json(obj, parent_key='', sep='.'):
            """Flatten nested JSON object"""
            items = []
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_key = f"{parent_key}{sep}{k}" if parent_key else k
                    if isinstance(v, (dict, list)):
                        items.extend(flatten_json(v, new_key, sep=sep).items())
                    else:
                        items.append((new_key, v))
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    new_key = f"{parent_key}[{i}]"
                    if isinstance(v, (dict, list)):
                        items.extend(flatten_json(v, new_key, sep=sep).items())
                    else:
                        items.append((new_key, v))
            return dict(items)
        
        # Flatten và convert thành text
        flattened = flatten_json(data)
        content_parts = [f"{key}: {value}" for key, value in flattened.items()]
        
        return content_parts, []
    except Exception as e:
        print(f"Error processing JSON file: {e}")
        return [], []