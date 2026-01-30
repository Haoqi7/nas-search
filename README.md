⚡ NAS Search - 极速离线数据查询系统一个专为 NAS（威联通/群晖）设计的海量文本数据查询方案。无依赖、零数据库、毫秒级响应。📖 项目简介在 NAS 上直接搜索巨大的文本文件（如 30GB+ 的社工库或日志）通常会导致系统卡死或耗时极长。本项目采用 Gzip 分片索引 (Gzip Sharding) 技术，将大文件物理切割并压缩为数千个小文件。核心优势：极速响应：查询时间 < 0.1秒。极高压缩：30GB 文本 -> 约 10-12GB 索引数据（节省 60%+ 空间）。零依赖：后端使用 Python 原生库，无需安装数据库，无需 pip install，无需联网。自动化：集成 GitHub Actions，自动构建并发布离线 Docker 镜像包。🏗️ 架构原理数据预处理：compress.py 读取原始 TXT，按号码/UID 前3位分片，存入 data_gzip/xxx.gz。后端服务：server.py (基于 http.server) 接收请求，直接定位并解压对应的单个 .gz 文件。前端交互：index.html 提供现代化搜索界面，支持状态检测、一键复制。📂 项目结构nas-search/
├── .github/workflows/
│   └── build-release.yml   # GitHub Action 自动化构建脚本
├── data_gzip/              # [重要] 本地生成的索引数据 (勿上传到 GitHub)
├── Dockerfile              # 镜像构建配置
├── server.py               # 零依赖后端服务
├── index.html              # 交互式前端
├── compress.py             # 数据处理/分片脚本
└── README.md               # 项目说明书
🚀 快速开始第一步：数据预处理 (推荐在高性能 PC/Mac 上进行)不要直接在 NAS 上处理数据（速度慢）。建议在电脑上挂载 NAS 磁盘后运行。修改 compress.py 中的 SOURCE_FOLDER 为你的 TXT 文件路径。运行脚本：python compress.py
等待完成，你将获得一个 data_gzip 文件夹。第二步：本地测试 (可选)在 data_gzip 同级目录下运行：python server.py
访问 http://localhost:8000/index.html 验证搜索是否正常。🐳 NAS 部署指南 (Docker)本项目支持 GitHub Action 自动化构建，您可以直接下载构建好的离线镜像包，无需在 NAS 上编译。方法 A：使用 Release 离线包 (推荐)下载镜像：前往本仓库的 Releases 页面，下载对应版本的镜像包 (例如 nas-search-2601.tar.gz)。导入 NAS：打开 Container Station -> 镜像 (Images) -> 导入 (Import)。选择下载的 .tar.gz 文件。上传数据：将第一步生成的 data_gzip 文件夹上传到 NAS (例如 /share/Container/SearchData/data_gzip)。创建容器：镜像选择：nas-search:2601挂载卷 (Volumes) [关键]：主机路径：/share/Container/SearchData/data_gzip (你的数据路径)容器路径：/data (必须是这个)端口映射：8090:8000方法 B：手动构建 (开发者)# 构建镜像
docker build -t nas-search:local .

# 运行容器
docker run -d \
  -p 8090:8000 \
  -v /你的本地数据路径/data_gzip:/data \
  --name nas-search \
  nas-search:local
🔄 版本发布流程 (CI/CD)本项目配置了 GitHub Actions。发布新版本只需打上 v 开头的标签。提交代码到 GitHub。打标签并推送：git tag v2601
git push origin v2601
