import http.server
import socketserver
import urllib.parse
import json
import os
import gzip
import sys

# 配置
PORT = 8000

# 智能寻找数据路径
def find_data_folder():
    # 1. 优先检查 Docker 挂载点 /data
    if os.path.exists("/data"):
        # 检查 /data 下是否有 .gz 文件
        if any(f.endswith('.gz') for f in os.listdir("/data")):
            return "/data"
    
    # 2. 检查当前目录下的 data_gzip (用于本地调试)
    local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_gzip")
    if os.path.exists(local_path):
        return local_path
        
    return None

DB_FOLDER = find_data_folder()

class SearchHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        
        # API: 状态检查
        if parsed.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            if DB_FOLDER:
                try:
                    count = len([f for f in os.listdir(DB_FOLDER) if f.endswith('.gz')])
                    self.wfile.write(json.dumps({"status": "ok", "count": count}).encode('utf-8'))
                except:
                    self.wfile.write(json.dumps({"status": "error", "msg": "Read Error"}).encode('utf-8'))
            else:
                self.wfile.write(json.dumps({"status": "error", "msg": "No Data Found"}).encode('utf-8'))
            return

        # API: 搜索
        elif parsed.path == '/api/search':
            qs = urllib.parse.parse_qs(parsed.query)
            q = qs.get('q', [''])[0].strip()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            res = []
            if DB_FOLDER and len(q) >= 3:
                fpath = os.path.join(DB_FOLDER, f"{q[:3]}.gz")
                if os.path.exists(fpath):
                    try:
                        with gzip.open(fpath, 'rt', encoding='utf-8') as f:
                            for line in f:
                                parts = line.strip().split(',')
                                if len(parts) >= 2 and (q == parts[0] or q == parts[1]):
                                    item = {"uid": parts[0], "phone": parts[1]}
                                    if item not in res: res.append(item)
                                    if len(res) >= 20: break
                    except: pass
            self.wfile.write(json.dumps(res).encode('utf-8'))
            return

        return http.server.SimpleHTTPRequestHandler.do_GET(self)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    socketserver.TCPServer.allow_reuse_address = True
    print(f"Server started on port {PORT}. Data folder: {DB_FOLDER}")
    with socketserver.TCPServer(("", PORT), SearchHandler) as httpd:
        httpd.serve_forever()