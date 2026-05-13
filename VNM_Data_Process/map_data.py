import json
import csv
import itertools
import re
from pathlib import Path

def sanitize_filename(filename):
    """
    Loại bỏ các ký tự không hợp lệ cho tên file trên Windows/Linux.
    """
    # Thay thế các ký tự cấm bằng dấu gạch ngang hoặc chuỗi rỗng
    safe_name = re.sub(r'[\\/*?:"<>|]', "", filename)
    #Cắt bớt tên thừa kể từ "chia theo" trở về sau
    safe_name = safe_name.split("chia theo")[0].strip()
    # Cắt bớt nếu tên quá dài (giới hạn an toàn khoảng 200 ký tự để chừa chỗ cho đường dẫn)
    return safe_name[:200].strip()

def json_stat_to_csv(json_filepath, clean_dir_path):
    try:
        # 1. Đọc và parse JSON (vẫn giữ logic chịu lỗi Extra data)
        with open(json_filepath, 'r', encoding='utf-8') as f:
            raw_text = f.read().strip()
            
        decoder = json.JSONDecoder()
        try:
            data, index = decoder.raw_decode(raw_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Không thể parse JSON: {e}")

        dataset = data.get('dataset')
        if not dataset:
            raise ValueError("File JSON không chứa node 'dataset' hợp lệ.")

        # 2. Lấy label làm tên file, nếu không có thì dùng tên file gốc
        original_stem = Path(json_filepath).stem
        dataset_label = dataset.get('label', original_stem)
        
        # Làm sạch tên file để tránh lỗi hệ điều hành
        safe_label = sanitize_filename(dataset_label)
        
        # Tạo đường dẫn file đích
        csv_filepath = clean_dir_path / f"{safe_label}.csv"

        # 3. Xử lý Metadata và Map dữ liệu (Giữ nguyên logic)
        dimensions_meta = dataset.get('dimension', {})
        dim_ids = dimensions_meta.get('id', []) 
        values = dataset.get('value', [])       

        dim_labels_list = []
        for dim_id in dim_ids:
            category = dimensions_meta[dim_id]['category']
            indices = category['index'] 
            labels = category['label']  
            
            ordered_labels = [None] * len(indices)
            for key, idx in indices.items():
                ordered_labels[idx] = labels[key]
                
            dim_labels_list.append(ordered_labels)

        headers = dim_ids + ["Giá trị"]
        rows = []
        combinations = list(itertools.product(*dim_labels_list))
        
        for i, combo in enumerate(combinations):
            val = values[i] if i < len(values) else ""
            rows.append(list(combo) + [val])

        # 4. Ghi file CSV
        with open(csv_filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
            
        return csv_filepath # Trả về đường dẫn để in log

    except Exception as e:
        print(f"  -> Lỗi khi xử lý file {Path(json_filepath).name}: {e}")
        return None

def process_all_files(raw_dir_str, clean_dir_str):
    raw_dir = Path(raw_dir_str)
    clean_dir = Path(clean_dir_str)
    clean_dir.mkdir(parents=True, exist_ok=True)

    json_files = list(raw_dir.glob("*.json"))
    
    if not json_files:
        print(f"Không tìm thấy file .json nào trong {raw_dir}")
        return

    print(f"Bắt đầu xử lý {len(json_files)} file...")

    for file_path in json_files:
        print(f"Đang đọc: {file_path.name}")
        output_path = json_stat_to_csv(file_path, clean_dir)
        
        if output_path:
            print(f"  -> Đã lưu thành công: {output_path.name}")

    print("Hoàn tất toàn bộ quá trình!")

# Chạy pipeline
if __name__ == "__main__":
    process_all_files("json", "raw")