import os

def count_total_lines(directory):
    total_lines = 0
    file_count = 0
    
    # 遍历目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        # 统计非空行（如果想统计所有行，改用 sum(1 for _ in f)）
                        lines = sum(1 for line in f if line.strip())
                        total_lines += lines
                        file_count += 1
                except Exception as e:
                    print(f"无法读取文件 {file_path}: {e}")
                    
    print(f"📂 扫描目录: {directory}")
    print(f"📄 Python 文件数量: {file_count}")
    print(f"📝 代码总行数 (非空): {total_lines}")

if __name__ == "__main__":
    # 统计当前目录
    count_total_lines(".")