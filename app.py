from flask import Flask, request, render_template, g
import sqlite3
import os

app = Flask(__name__)

# --- 关键配置 ---
# 容器内部固定的数据库路径
# 我们会在 NAS 设置里把真实路径挂载到这里的 /data
DATABASE = '/data/data_search.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        # 检查文件是否存在，避免报错直接崩溃
        if not os.path.exists(DATABASE):
            return None
        # 连接数据库
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    search_term = ""
    error = None
    db_status = "正常"
    
    # 检查数据库连接状态
    if not os.path.exists(DATABASE):
        db_status = f"❌ 未连接 (请确保NAS挂载路径正确，且容器内路径为 /data，当前寻找: {DATABASE})"
    
    if request.method == 'POST':
        search_term = request.form.get('query', '').strip()
        conn = get_db()
        
        if not conn:
            error = "无法读取数据库文件，请检查 Docker 挂载设置。"
        elif search_term:
            try:
                cur = conn.cursor()
                # 核心查询逻辑：同时查 Phone 和 UID
                sql = "SELECT uid, phone FROM users WHERE phone = ? OR uid = ?"
                cur.execute(sql, (search_term, search_term))
                results = cur.fetchall()
                if not results:
                    error = "未找到匹配的数据"
            except Exception as e:
                error = f"查询发生错误: {e}"

    return render_template('index.html', results=results, search_term=search_term, error=error, db_status=db_status)

if __name__ == '__main__':
    # 监听 5000 端口
    app.run(host='0.0.0.0', port=5000)