# 使用超轻量级 Python 基础镜像 (仅 15MB 左右)
FROM python:3.9.25-alpine

# 设置工作目录
WORKDIR /app

# 复制当前目录下的所有文件到容器的 /app
# (.gitignore 里的文件会被自动忽略，不会复制进去)
COPY . /app

# 声明数据卷挂载点 (告诉用户这里需要挂载数据)
VOLUME /data

# 设置环境变量，告诉 server.py 数据在哪里
ENV DATA_PATH=/data

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "server.py"]
