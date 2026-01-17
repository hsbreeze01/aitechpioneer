# RAG 文档问答系统 - 用户手册

## 目录

1. [系统概述](#系统概述)
2. [系统架构](#系统架构)
3. [功能特性](#功能特性)
4. [部署指南](#部署指南)
5. [启动方式](#启动方式)
6. [使用指南](#使用指南)
7. [故障排查](#故障排查)
8. [API 文档](#api-文档)
9. [常见问题](#常见问题)

---

## 系统概述

RAG（Retrieval-Augmented Generation）文档问答系统是一个基于大语言模型的智能文档检索和问答平台。系统通过语义向量检索技术，帮助用户快速找到文档中的相关信息，并生成准确的答案。

### 核心特性

- 📄 **多格式文档支持**：PDF、TXT、Markdown、DOCX
- 🧩 **智能分块**：自动将文档分割成语义相关的块
- 🔍 **语义检索**：基于向量相似度的智能搜索
- 💬 **AI 问答**：结合检索结果生成准确答案
- 📊 **数据管理**：完整的文档和 Chunk 管理功能
- 🎨 **现代化 UI**：响应式设计，优秀的用户体验

### 技术栈

| 组件 | 技术 |
|--------|------|
| 后端框架 | FastAPI |
| 向量数据库 | Qdrant |
| 大语言模型 | DeepSeek |
| 嵌入模型 | BGE (本地/云端) |
| 前端 | HTML/CSS/JavaScript |
| 文档解析 | PyPDF2、python-docx |

---

## 系统架构

### 分层架构

```
┌─────────────────────────────────────────────────────────────┐
│                   Interfaces Layer                      │
│  (HTTP API, CLI, User Interaction)                   │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                 Application Layer                      │
│         (Use Cases, Business Logic)                  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Domain Layer                         │
│      (Models, Business Rules, Ports)                 │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Infrastructure Layer                      │
│  (Database, External APIs, Third-party Services)      │
└───────────────────────────────────────────────────────────┘
```

### 目录结构

```
aitechpioneer/
├── frontend/              # 前端文件
│   ├── static/          # 静态资源
│   │   ├── css/       # 样式文件
│   │   ├── js/        # JavaScript 文件
│   │   └── icons/     # SVG 图标
│   ├── index.html       # 首页
│   ├── documents.html   # 文档管理
│   ├── upload.html      # 上传文档
│   ├── qa.html         # 智能问答
│   ├── search.html      # 智能检索
│   ├── chunks.html      # Chunk 管理
│   └── admin.html      # 管理员控制台
├── src/
│   └── aitechpioneer/
│       ├── application/   # 应用层
│       ├── domain/        # 领域层
│       ├── infrastructure/ # 基础设施层
│       └── interfaces/    # 接口层
├── docs/              # 文档
├── scripts/           # 工具脚本
├── tests/             # 测试
├── .env               # 环境配置
└── pyproject.toml      # 项目配置
```

### 依赖规则

- ✅ **允许的依赖**：
  - `interfaces` → `application`
  - `application` → `domain`（通过接口）
  - `infrastructure` → `domain` / `application`

- ❌ **禁止的依赖**：
  - `domain` → `application` / `infrastructure` / `interfaces`
  - `application` → `infrastructure`（直接依赖）

---

## 功能特性

### 1. 文档管理

#### 上传文档
- 支持拖拽上传
- 异步处理大文件
- 实时进度显示
- 支持格式：PDF、TXT、Markdown、DOCX

#### 文档列表
- 查看所有上传的文档
- 显示文档元数据（文件名、类型、上传时间、Chunk 数量）
- 快速跳转到文档详情

#### 文档详情
- 查看文档完整信息
- 浏览所有 Chunk
- 编辑 Chunk 内容
- 删除 Chunk

### 2. 智能问答

#### 提问功能
- 自然语言提问
- 自定义检索参数（Top-K、相似度阈值）
- 实时生成答案
- 显示相关 Chunk 来源

#### 答案反馈
- 满意/不满意反馈
- 评分系统（1-5 分）
- 提供评论建议
- 问题解决状态标记

#### 问答历史
- 查看历史问答记录
- 按时间筛选（今天、最近一周）
- 统计信息展示

### 3. 智能检索

#### 语义搜索
- 基于向量相似度的检索
- 自定义检索参数
- 显示相似度分数
- 快速复制内容

#### 高级筛选
- 按 Chunk 状态筛选
- 按 Chunk 类型筛选
- 按文档 ID 定位

### 4. Chunk 管理

#### Chunk 列表
- 查看所有 Chunk
- 显示 Chunk 元数据
- 批量操作支持

#### Chunk 合并
- 手动选择合并
- 相邻 Chunk 快速合并
- 合并预览
- 撤销合并

#### 语义重切分
- 基于语义的智能分割
- 自定义 Chunk 大小
- 保留原始 Chunk

#### Chunk 编辑
- 修改 Chunk 内容
- 更新 Chunk 状态
- 标记删除原因

### 5. 管理员控制台

#### 不满意记录
- 查看用户不满意的问答
- 分析问题原因
- 优化 Chunk 质量

---

## 部署指南

### 环境要求

#### 系统要求
- **操作系统**：Linux、macOS、Windows
- **Python 版本**：3.11 或更高
- **内存**：至少 4GB RAM（推荐 8GB+）
- **磁盘空间**：至少 10GB 可用空间

#### 依赖服务
- **Qdrant**：向量数据库（可选 Docker）
- **DeepSeek API**：大语言模型服务
- **SiliconFlow API**：嵌入模型服务（可选）

### 安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd aitechpioneer
```

#### 2. 创建虚拟环境

```bash
# 使用 venv
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 或使用 conda
conda create -n aitechpioneer python=3.11
conda activate aitechpioneer
```

#### 3. 安装依赖

```bash
pip install -e .
```

或手动安装：

```bash
pip install fastapi uvicorn qdrant-client pydantic pydantic-settings
pip install python-dotenv httpx aiohttp
pip install sentence-transformers torch
pip install python-multipart pypdf python-docx markdown
pip install pytesseract pdf2image pillow
```

#### 4. 配置环境变量

复制示例配置文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置以下参数：

```bash
# Qdrant 配置
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=

# DeepSeek API
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# SiliconFlow API（可选）
SILICONFLOW_API_KEY=your_siliconflow_api_key_here
EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5
EMBEDDING_API_URL=https://api.siliconflow.cn/v1/embeddings

# 本地嵌入模型（推荐）
USE_LOCAL_EMBEDDING=True
LOCAL_EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5

# 日志配置
LOG_LEVEL=INFO
DEBUG=False
```

#### 5. 启动 Qdrant

**方式一：使用 Docker（推荐）**

```bash
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant:latest
```

**方式二：本地安装**

参考 [Qdrant 官方文档](https://qdrant.tech/documentation/) 进行安装。

#### 6. 初始化数据库

首次启动会自动创建必要的集合和索引。

---

## 启动方式

### 开发模式

使用 `uvicorn` 启动开发服务器：

```bash
python3 -m uvicorn aitechpioneer.interfaces.api:app --host 0.0.0.0 --port 8000 --reload
```

参数说明：
- `--host 0.0.0.0`：监听所有网络接口
- `--port 8000`：指定端口
- `--reload`：代码变更自动重载

### 生产模式

使用 `gunicorn` 启动生产服务器：

```bash
pip install gunicorn
gunicorn aitechpioneer.interfaces.api:app \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --worker-class uvicorn.workers.UvicornWorker
```

### 使用 systemd（Linux）

创建服务文件 `/etc/systemd/system/aitechpioneer.service`：

```ini
[Unit]
Description=RAG System API
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/aitechpioneer
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn aitechpioneer.interfaces.api:app --workers 4 --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl enable aitechpioneer
sudo systemctl start aitechpioneer
sudo systemctl status aitechpioneer
```

### 使用 Docker Compose

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - ./qdrant_storage:/qdrant/storage

  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - qdrant
    environment:
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
    volumes:
      - ./frontend:/app/frontend
```

启动：

```bash
docker-compose up -d
```

---

## 使用指南

### 访问系统

启动成功后，在浏览器中访问：

- **首页**：http://localhost:8000/index.html
- **API 文档**：http://localhost:8000/docs
- **交互式 API**：http://localhost:8000/redoc

### 基本工作流程

#### 1. 上传文档

1. 访问"上传文档"页面
2. 拖拽文件到上传区域或点击选择文件
3. 填写文档标题和描述（可选）
4. 点击"上传文档"
5. 在任务列表中查看处理进度

#### 2. 智能问答

1. 访问"智能问答"页面
2. 在输入框中输入问题
3. 调整检索参数（可选）
4. 点击"提问"按钮
5. 查看生成的答案和相关 Chunk
6. 对答案进行反馈（满意/不满意）

#### 3. Chunk 管理

1. 访问"Chunk 管理"页面
2. 使用筛选器查找目标 Chunk
3. 选择需要合并的 Chunk
4. 点击"合并"按钮
5. 确认合并预览
6. 查看合并结果

#### 4. 语义检索

1. 访问"智能检索"页面
2. 输入检索关键词或问题
3. 调整检索参数
4. 点击"检索"按钮
5. 查看相似度最高的 Chunk
6. 复制需要的内容

### API 使用示例

#### 上传文档

```bash
curl -X POST "http://localhost:8000/api/documents/upload-async" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf" \
  -F "file_type=pdf" \
  -F "collection_name=documents"
```

#### 智能问答

```bash
curl -X POST "http://localhost:8000/api/questions/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "什么是 RAG？",
    "collection_name": "documents",
    "limit": 5,
    "score_threshold": 0.5
  }'
```

#### 获取文档列表

```bash
curl -X GET "http://localhost:8000/api/documents"
```

#### 获取 Chunk 列表

```bash
curl -X GET "http://localhost:8000/api/chunks"
```

---

## 故障排查

### 常见问题

#### 1. 服务无法启动

**症状**：运行启动命令后服务立即退出

**可能原因**：
- 端口被占用
- 依赖未安装
- 环境变量配置错误

**解决方案**：

```bash
# 检查端口占用
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# 更换端口
python3 -m uvicorn aitechpioneer.interfaces.api:app --port 8001

# 检查依赖
pip list | grep -E "(fastapi|uvicorn|qdrant)"

# 验证环境变量
python3 -c "from aitechpioneer.settings import settings; print(settings)"
```

#### 2. Qdrant 连接失败

**症状**：启动时出现 Qdrant 连接错误

**可能原因**：
- Qdrant 未启动
- Qdrant 地址配置错误
- 防火墙阻止连接

**解决方案**：

```bash
# 检查 Qdrant 是否运行
curl http://localhost:6333/health

# 检查 Docker 容器
docker ps | grep qdrant

# 查看 Qdrant 日志
docker logs qdrant

# 重启 Qdrant
docker restart qdrant
```

#### 3. 嵌入模型加载失败

**症状**：上传文档时嵌入模型加载失败

**可能原因**：
- 模型文件损坏
- 磁盘空间不足
- 内存不足

**解决方案**：

```bash
# 检查磁盘空间
df -h

# 检查内存使用
free -h  # Linux
vm_stat  # macOS

# 清理缓存
rm -rf ~/.cache/huggingface/

# 重新下载模型
python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-zh-v1.5')"
```

#### 4. DeepSeek API 调用失败

**症状**：问答时出现 API 错误

**可能原因**：
- API Key 无效
- API 配额用尽
- 网络连接问题

**解决方案**：

```bash
# 验证 API Key
curl -X POST "https://api.deepseek.com/v1/chat/completions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek-chat", "messages": [{"role": "user", "content": "Hello"}]}'

# 检查网络连接
ping api.deepseek.com

# 查看详细错误日志
# 设置 LOG_LEVEL=DEBUG
```

#### 5. 前端页面无法加载

**症状**：浏览器访问页面显示错误

**可能原因**：
- 静态文件路径错误
- CORS 配置问题
- 浏览器缓存

**解决方案**：

```bash
# 检查静态文件
ls -la frontend/static/

# 清除浏览器缓存
# Chrome: Ctrl+Shift+Delete
# Firefox: Ctrl+Shift+Delete

# 检查 CORS 配置
# 确认 api.py 中的 CORSMiddleware 配置
```

#### 6. 文档上传失败

**症状**：上传文档时出现错误

**可能原因**：
- 文件格式不支持
- 文件过大
- 文件损坏

**解决方案**：

```bash
# 检查文件类型
file document.pdf

# 检查文件大小
ls -lh document.pdf

# 验证文件完整性
pdfinfo document.pdf  # PDF
head -n 10 document.txt  # TXT

# 查看上传任务日志
# 检查 task_manager 日志
```

#### 7. 检索结果不准确

**症状**：检索到的 Chunk 与问题不相关

**可能原因**：
- 相似度阈值设置过高
- Chunk 分割不合理
- 嵌入模型不匹配

**解决方案**：

```bash
# 调整相似度阈值
# 降低 score_threshold 到 0.3-0.5

# 重新分块文档
# 使用语义重切分功能

# 更换嵌入模型
# 在 .env 中更改 LOCAL_EMBEDDING_MODEL
```

### 日志查看

#### 启用调试日志

在 `.env` 文件中设置：

```bash
LOG_LEVEL=DEBUG
DEBUG=True
```

#### 查看日志输出

```bash
# 启动时查看实时日志
python3 -m uvicorn aitechpioneer.interfaces.api:app --log-level debug

# 保存日志到文件
python3 -m uvicorn aitechpioneer.interfaces.api:app > app.log 2>&1

# 使用 systemd 查看日志
sudo journalctl -u aitechpioneer -f
```

### 性能优化

#### 1. 数据库优化

```bash
# Qdrant 配置优化
# 增加内存限制
docker run -d --name qdrant \
  -e QDRANT__SERVICE__GRPC_PORT=6334 \
  -e QDRANT__STORAGE__PERFORMANCE__MAX_OPTIMIZATION_THREADS=4 \
  qdrant/qdrant:latest
```

#### 2. 应用优化

```bash
# 增加工作进程
gunicorn aitechpioneer.interfaces.api:app --workers 8

# 使用异步 I/O
# 确保使用 asyncio 和 aiohttp

# 启用缓存
# 在 settings.py 中配置缓存
```

#### 3. 前端优化

```bash
# 压缩静态资源
# 使用 gzip 或 brotli

# 启用 CDN
# 将静态文件部署到 CDN

# 使用 HTTP/2
# 配置 Nginx 支持 HTTP/2
```

---

## API 文档

### 端点列表

#### 文档管理

| 方法 | 端点 | 描述 |
|------|--------|------|
| GET | `/api/documents` | 获取文档列表 |
| POST | `/api/documents/upload-async` | 异步上传文档 |
| GET | `/api/documents/{document_id}` | 获取文档详情 |
| DELETE | `/api/documents/{document_id}` | 删除文档 |

#### Chunk 管理

| 方法 | 端点 | 描述 |
|------|--------|------|
| GET | `/api/chunks` | 获取 Chunk 列表 |
| GET | `/api/chunks/{chunk_id}` | 获取 Chunk 详情 |
| PUT | `/api/chunks/{chunk_id}/status` | 更新 Chunk 状态 |
| DELETE | `/api/chunks/{chunk_id}` | 删除 Chunk |
| POST | `/api/chunks/merge` | 合并 Chunk |
| POST | `/api/chunks/merge/preview` | 预览合并 |
| POST | `/api/chunks/merge/undo` | 撤销合并 |
| POST | `/api/chunks/{chunk_id}/merge-forward` | 向前合并 |
| POST | `/api/chunks/{chunk_id}/merge-backward` | 向后合并 |
| POST | `/api/documents/{document_id}/semantic-resegment` | 语义重切分 |

#### 问答系统

| 方法 | 端点 | 描述 |
|------|--------|------|
| POST | `/api/questions/answer` | 智能问答 |
| GET | `/api/qa/records` | 获取问答记录 |
| GET | `/api/qa/records/chunk/{chunk_id}` | 获取 Chunk 的问答记录 |
| GET | `/api/qa/records/document/{document_id}` | 获取文档的问答记录 |
| GET | `/api/qa/records/unsatisfied` | 获取不满意的记录 |
| POST | `/api/qa/feedback` | 提交反馈 |

#### 上传任务

| 方法 | 端点 | 描述 |
|------|--------|------|
| GET | `/api/upload-tasks` | 获取上传任务列表 |
| POST | `/api/upload-tasks/{task_id}/retry` | 重试任务 |
| DELETE | `/api/upload-tasks/{task_id}` | 删除任务 |

### 完整 API 文档

访问 http://localhost:8000/docs 查看完整的交互式 API 文档。

---

## 常见问题

### Q1: 系统支持哪些文档格式？

**A**：目前支持 PDF、TXT、Markdown 和 DOCX 格式。

### Q2: 如何提高检索准确率？

**A**：
- 调整相似度阈值（降低到 0.3-0.5）
- 使用语义重切分优化 Chunk
- 选择合适的嵌入模型
- 增加 Top-K 值获取更多候选

### Q3: 系统的硬件要求是什么？

**A**：
- 最低：4GB RAM，双核 CPU
- 推荐：8GB+ RAM，四核 CPU
- 大规模部署：16GB+ RAM，GPU 加速

### Q4: 如何备份数据？

**A**：
```bash
# 备份 Qdrant 数据
docker cp qdrant:/qdrant/storage ./backup/qdrant

# 备份应用配置
cp .env ./backup/
cp -r frontend ./backup/
```

### Q5: 如何升级系统？

**A**：
```bash
# 拉取最新代码
git pull origin main

# 更新依赖
pip install -e .

# 重启服务
sudo systemctl restart aitechpioneer
```

### Q6: 系统是否支持多语言？

**A**：目前主要优化中文，但支持多语言。选择合适的嵌入模型可以获得更好的效果。

### Q7: 如何监控系统性能？

**A**：
- 使用 API 文档的 `/health` 端点
- 查看 Qdrant 统计信息
- 监控系统资源使用
- 分析日志文件

### Q8: 如何联系技术支持？

**A**：
- 提交 Issue 到项目仓库
- 查看文档和 FAQ
- 加入社区讨论

---

## 附录

### A. 环境变量完整列表

| 变量名 | 类型 | 默认值 | 描述 |
|---------|------|----------|------|
| `QDRANT_HOST` | string | localhost | Qdrant 服务器地址 |
| `QDRANT_PORT` | int | 6333 | Qdrant 服务器端口 |
| `QDRANT_API_KEY` | string | "" | Qdrant API 密钥 |
| `DEEPSEEK_API_KEY` | string | "" | DeepSeek API 密钥 |
| `SILICONFLOW_API_KEY` | string | "" | SiliconFlow API 密钥 |
| `EMBEDDING_MODEL` | string | BAAI/bge-large-zh-v1.5 | 云端嵌入模型 |
| `EMBEDDING_API_URL` | string | https://api.siliconflow.cn/v1/embeddings | 嵌入 API 地址 |
| `USE_LOCAL_EMBEDDING` | bool | True | 是否使用本地嵌入 |
| `LOCAL_EMBEDDING_MODEL` | string | BAAI/bge-small-zh-v1.5 | 本地嵌入模型 |
| `LOG_LEVEL` | string | INFO | 日志级别 |
| `DEBUG` | bool | False | 调试模式 |

### B. 端口使用

| 端口 | 服务 | 说明 |
|-------|------|------|
| 8000 | FastAPI | Web 服务端口 |
| 6333 | Qdrant HTTP | Qdrant HTTP API |
| 6334 | Qdrant gRPC | Qdrant gRPC API |

### C. 参考资源

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Qdrant 文档](https://qdrant.tech/documentation/)
- [DeepSeek API](https://platform.deepseek.com/api-docs/)
- [Sentence Transformers](https://www.sbert.net/)

---

**版本**：0.1.0  
**更新日期**：2025-01-17  
**维护者**：AI Tech Pioneer Team
