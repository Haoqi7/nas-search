import os
import re
import time
import gzip
import sys

# ================= 配置区域 =================
# 输入路径：SMB 挂载的盘符
SOURCE_FOLDER = r"/Users/hao/Desktop/q"  
# 输出路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FOLDER = os.path.join(BASE_DIR, "data_gzip")
# 进度记录文件 (关键！)
PROGRESS_LOG = os.path.join(BASE_DIR, "processed_files.log")
# ===========================================

def parse_line(line):
    line = line.strip()
    if not line: return None, None
    if '-' in line: 
        parts = re.split(r'-+', line)
        if len(parts) >= 2: return parts[0].strip(), parts[1].strip()
    else: 
        parts = line.split()
        if len(parts) >= 2: return parts[1].strip(), parts[0].strip()
    return None, None

def load_processed_files():
    """读取已经处理完的文件列表"""
    if not os.path.exists(PROGRESS_LOG):
        return set()
    with open(PROGRESS_LOG, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f)

def mark_file_as_done(filename):
    """标记某个文件已完成"""
    with open(PROGRESS_LOG, 'a', encoding='utf-8') as f:
        f.write(f"{filename}\n")

def main():
    print(f"🚀 [断点续传版 V3] 开始处理...")
    print(f"📂 读取源: {SOURCE_FOLDER}")
    
    if not os.path.exists(SOURCE_FOLDER):
        print(f"❌ 错误：找不到路径 {SOURCE_FOLDER}")
        return
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # 1. 获取所有源文件
    all_files = [f for f in os.listdir(SOURCE_FOLDER) if f.lower().endswith('.txt')]
    if not all_files:
        print("❌ 未找到 txt 文件")
        return

    # 2. 读取进度记录 (核心逻辑)
    processed_files = load_processed_files()
    print(f"📋 历史记录: 已完成 {len(processed_files)} 个文件")

    # 过滤掉已经处理的文件
    files_to_process = [f for f in all_files if f not in processed_files]
    
    if not files_to_process:
        print("🎉 所有文件都已处理完毕！无需操作。")
        return

    print(f"📊 本次待处理: {len(files_to_process)} 个文件 (跳过了 {len(processed_files)} 个)")
    print("-" * 50)

    # 3. 开始处理
    BUFFER_LIMIT = 500000 
    buffer = {}
    
    for idx, file_name in enumerate(files_to_process):
        file_path = os.path.join(SOURCE_FOLDER, file_name)
        file_size = os.path.getsize(file_path)
        
        print(f"👉 [{idx+1}/{len(files_to_process)}] 正在处理: {file_name} ({file_size/(1024*1024):.1f} MB)")
        
        # 编码尝试
        encodings = ['utf-8', 'gb18030', 'gbk', 'latin-1']
        f = None
        for enc in encodings:
            try:
                f = open(file_path, 'r', encoding=enc, errors='ignore')
                f.readline(); f.seek(0)
                break
            except: f = None
        
        if not f:
            print(f"⚠️ 无法识别编码，跳过: {file_name}")
            mark_file_as_done(file_name) # 无法读取也标记为完成，避免卡死
            continue

        # 读取文件内容
        line_count = 0
        with f:
            for line in f:
                uid, phone = parse_line(line)
                if uid and phone:
                    row = f"{uid},{phone}\n"
                    # 双向存储
                    u_key = uid[:3] if len(uid) >= 3 else "misc"
                    if u_key not in buffer: buffer[u_key] = []
                    buffer[u_key].append(row)
                    
                    p_key = phone[:3] if len(phone) >= 3 else "misc"
                    if p_key not in buffer: buffer[p_key] = []
                    buffer[p_key].append(row)
                    
                    line_count += 1
                
                # 定期写入硬盘，防止内存溢出
                if line_count % BUFFER_LIMIT == 0:
                    flush_buffer(buffer, OUTPUT_FOLDER)
                    sys.stdout.write(f"\r   ...已缓冲 {line_count} 行")
                    sys.stdout.flush()
        
        # 一个文件彻底处理完后，清空剩余缓存，并记录到日志
        flush_buffer(buffer, OUTPUT_FOLDER)
        mark_file_as_done(file_name) # <--- 关键：处理完一个，记账一个
        print(f"\n✅ {file_name} 完成。")

    print(f"\n🎉 所有任务全部完成！")

def flush_buffer(buf, output_folder):
    for bucket_key, lines in buf.items():
        file_path = os.path.join(output_folder, f"{bucket_key}.gz")
        try:
            with gzip.open(file_path, 'at', encoding='utf-8') as gf:
                gf.writelines(lines)
        except Exception as e:
            pass
    buf.clear()

if __name__ == "__main__":
    main()
