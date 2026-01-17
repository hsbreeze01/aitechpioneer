# RAG 文档问答系统

> 基于 DeepSeek 和 Qdrant 的智能文档检索与问答平台

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 目录

- [系统简介](#系统简介)
- [核心特性](#核心特性)
- [快速开始](#快速开始)
- [系统架构](#系统架构)
- [部署指南](#部署指南)
- [使用文档](#使用文档)
- [故障排查](#故障排查)
- [开发指南](#开发指南)

---

## 系统简介

RAG（Retrieval-Augmented Generation）文档问答系统是一个企业级的智能文档检索和问答平台。系统通过语义向量检索技术，结合大语言模型，为用户提供准确、快速的文档问答服务。

### 技术亮点

- 🚀 **高性能**：基于 FastAPI 和 Qdrant 的异步架构
- 🧠 **智能检索**：使用 BGE 嵌入模型进行语义搜索
- 💬 **AI 问答**：集成 DeepSeek 大语言模型
- 📊 **数据管理**：完整的文档和 Chunk 生命周期管理
- 🎨 **现代化 UI**：响应式设计，优秀的用户体验
- 🔧 **可扩展**：模块化架构，易于扩展和维护

### 技术栈

| 层级 | 技术 | 用途 |
|--------|------|------|
| **接口层** | FastAPI | RESTful API 服务 |
| **应用层** | Python Use Cases | 业务逻辑编排 |
| **领域层** | Pydantic Models | 领域模型定义 |
| **基础设施层** | Qdrant, DeepSeek | 数据存储和外部服务 |
| **前端** | HTML/CSS/JS | 用户界面 |

---

## 核心特性

### 📄 文档管理

- **多格式支持**：PDF、TXT、Markdown、DOCX
- **异步上传**：大文件异步处理，实时进度显示
- **智能解析**：自动提取文档内容和元数据
- **版本管理**：文档版本追踪和历史记录

### 🧩 Chunk 管理

- **智能分块**：基于语义的文档分割
- **灵活合并**：支持手动和自动合并策略
- **语义重切分**：基于语义边界的智能重新分割
- **状态管理**：活跃、已弃用、非活跃状态

### 🔍 智能检索

- **语义搜索**：基于向量相似度的精准检索
- **高级筛选**：按状态、类型、文档筛选
- **相似度控制**：可配置的相似度阈值
- **批量操作**：支持批量查看和操作

### 💬 智能问答

- **自然语言**：支持自然语言提问
- **上下文感知**：结合检索结果生成准确答案
- **反馈机制**：用户满意度收集和问题追踪
- **历史记录**：完整的问答历史和统计

### 📊 数据分析

- **统计面板**：文档、Chunk、问答统计
- **质量监控**：Chunk 质量评分和优化建议
- **使用分析**：检索频率和热点内容分析

---

## 快速开始

### 环境要求

- **Python**：3.11 或更高版本
- **内存**：至少 4GB RAM（推荐 8GB+）
- **磁盘**：至少 10GB 可用空间
- **操作系统**：Linux、macOS、Windows

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

#### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置必要的 API 密钥
```

#### 5. 启动 Qdrant（使用 Docker）

```bash
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant:latest
```

#### 6. 启动服务

```bash
python3 -m uvicorn aitechpioneer.interfaces.api:app --host 0.0.0.0 --port 8000 --reload
```

#### 7. 访问系统

打开浏览器访问：
- **首页**：http://localhost:8000/index.html
- **API 文档**：http://localhost:8000/docs

---

## 系统架构

### 分层架构

系统采用严格的分层架构，确保代码的可维护性和可测试性：

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
│   │   └── icons/     # SVG 图标库
│   ├── index.html       # 首页
│   ├── documents.html   # 文档管理
│   ├── upload.html      # 上传文档
│   ├── qa.html         # 智能问答
│   ├── search.html      # 智能检索
│   ├── chunks.html      # Chunk 管理
│   └── admin.html      # 管理员控制台
├── src/
│   └── aitechpioneer/
│       ├── application/   # 应用层（用例）
│       ├── domain/        # 领域层（模型、规则）
│       ├── infrastructure/ # 基础设施层（数据库、API）
│       └── interfaces/    # 接口层（HTTP、CLI）
├── docs/              # 项目文档
│   ├── architecture.md  # 架构规范
│   ├── design-system.md # 设计系统
│   └── ui-ux-workflow.md # UI/UX 工作流
├── scripts/           # 工具脚本
│   ├── validate_spec.py # Spec 验证
│   ├── validate_structure.py # 结构验证
│   └── validate_ui_ux.py # UI/UX 验证
├── tests/             # 测试文件
├── .env               # 环境配置
├── .env.example       # 环境配置示例
├── pyproject.toml      # 项目配置
├── README.md          # 项目说明（本文件）
└── USER_GUIDE.md      # 用户手册
```

### 依赖规则

**允许的依赖**：
- ✅ `interfaces` → `application`
- ✅ `application` → `domain`（通过接口）
- ✅ `infrastructure` → `domain` / `application`

**禁止的依赖**：
- ❌ `domain` → `application` / `infrastructure` / `interfaces`
- ❌ `application` → `infrastructure`（直接依赖）

---

## 部署指南

### 开发环境

#### 快速启动

```bash
# 1. 启动 Qdrant
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant:latest

# 2. 启动应用
python3 -m uvicorn aitechpioneer.interfaces.api:app --host 0.0.0.0 --port 8000 --reload
```

#### 配置说明

编辑 `.env` 文件：

```bash
# Qdrant 配置
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=

# DeepSeek API（必需）
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# SiliconFlow API（可选，用于云端嵌入）
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

### 生产环境

#### 使用 Gunicorn

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动服务
gunicorn aitechpioneer.interfaces.api:app \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --worker-class uvicorn.workers.UvicornWorker \
  --access-logfile - \
  --error-logfile -
```

#### 使用 Systemd（Linux）

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
ExecStart=/path/to/venv/bin/gunicorn aitechpioneer.interfaces.api:app \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --worker-class uvicorn.workers.UvicornWorker
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

管理服务：

```bash
# 启用服务
sudo systemctl enable aitechpioneer

# 启动服务
sudo systemctl start aitechpioneer

# 查看状态
sudo systemctl status aitechpioneer

# 查看日志
sudo journalctl -u aitechpioneer -f
```

#### 使用 Docker Compose

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - ./qdrant_storage:/qdrant/storage
    restart: unless-stopped

  app:
    build: .
    container_name: aitechpioneer
    ports:
      - "8000:8000"
    depends_on:
      - qdrant
    environment:
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - USE_LOCAL_EMBEDDING=True
    volumes:
      - ./frontend:/app/frontend
      - ./.env:/app/.env
    restart: unless-stopped
```

启动：

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### Nginx 反向代理

配置 Nginx 作为反向代理：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/aitechpioneer/frontend;
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket 支持（如果需要）
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 使用文档

### 快速上手

#### 1. 上传第一个文档

1. 访问 http://localhost:8000/upload.html
2. 拖拽 PDF 文件到上传区域
3. 点击"上传文档"
4. 等待处理完成

#### 2. 进行智能问答

1. 访问 http://localhost:8000/qa.html
2. 输入问题："这个系统的主要功能是什么？"
3. 点击"提问"
4. 查看生成的答案和相关 Chunk

#### 3. 管理 Chunk

1. 访问 http://localhost:8000/chunks.html
2. 查看所有 Chunk
3. 选择两个 Chunk 进行合并
4. 点击"合并"按钮

### 详细使用指南

完整的用户手册请参考 [USER_GUIDE.md](USER_GUIDE.md)，包含：

- 📚 详细的功能说明
- 🎯 操作指南和最佳实践
- 🔧 高级配置和优化
- ❓ 常见问题解答

---

## 故障排查

### 常见问题

#### 1. 服务无法启动

**症状**：运行启动命令后立即退出

**解决方案**：

```bash
# 检查端口占用
lsof -i :8000  # Linux/macOS

# 检查依赖
pip list | grep -E "(fastapi|uvicorn|qdrant)"

# 查看详细错误
LOG_LEVEL=DEBUG python3 -m uvicorn aitechpioneer.interfaces.api:app
```

#### 2. Qdrant 连接失败

**症状**：启动时出现连接错误

**解决方案**：

```bash
# 检查 Qdrant 是否运行
curl http://localhost:6333/health

# 查看 Docker 容器状态
docker ps -a | grep qdrant

# 重启 Qdrant
docker restart qdrant
```

#### 3. API 调用失败

**症状**：问答或上传时出现 API 错误

**解决方案**：

```bash
# 验证 API Key
python3 -c "from aitechpioneer.settings import settings; print(settings.deepseek_api_key)"

# 检查网络连接
ping api.deepseek.com

# 查看详细日志
# 设置 LOG_LEVEL=DEBUG
```

#### 4. 前端页面无法加载

**症状**：浏览器显示 404 或错误

**解决方案**：

```bash
# 检查静态文件路径
ls -la frontend/static/

# 清除浏览器缓存
# Ctrl+Shift+Delete (Chrome/Firefox)

# 检查 CORS 配置
# 确认 api.py 中的 CORSMiddleware 设置
```

### 日志和调试

#### 启用调试模式

在 `.env` 文件中设置：

```bash
LOG_LEVEL=DEBUG
DEBUG=True
```

#### 查看日志

```bash
# 实时日志
python3 -m uvicorn aitechpioneer.interfaces.api:app --log-level debug

# 保存到文件
python3 -m uvicorn aitechpioneer.interfaces.api:app > app.log 2>&1

# Systemd 日志
sudo journalctl -u aitechpioneer -f
```

### 性能优化

#### 数据库优化

```bash
# 增加 Qdrant 内存限制
docker run -d \
  -e QDRANT__STORAGE__PERFORMANCE__MAX_OPTIMIZATION_THREADS=4 \
  qdrant/qdrant:latest
```

#### 应用优化

```bash
# 增加工作进程
gunicorn aitechpioneer.interfaces.api:app --workers 8

# 启用缓存
# 在应用层实现缓存策略
```

---

## 开发指南

### 代码规范

#### 架构规则

所有代码必须遵循 [docs/architecture.md](docs/architecture.md) 中定义的分层架构。

**重要原则**：
- 严格遵循分层架构
- 禁止跨层反向依赖
- 领域层不依赖其他层

#### 代码风格

```bash
# 格式化代码
black src/

# 检查代码质量
ruff check src/

# 类型检查
mypy src/
```

### 测试

#### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_chunk_merge.py

# 生成覆盖率报告
pytest --cov=aitechpioneer tests/
```

#### 验证脚本

```bash
# 验证 Spec
python3 scripts/validate_spec.py

# 验证项目结构
python3 scripts/validate_structure.py

# 验证 UI/UX
python3 scripts/validate_ui_ux.py
```

### 添加新功能

#### 1. 定义 Spec

在 `spec/` 目录下创建新的 spec 文件：

```markdown
# Feature Name

## Requirements
- Requirement 1
- Requirement 2

## Design
- Design decision 1
- Design decision 2

## Tasks
- [ ] Task 1
- [ ] Task 2
```

#### 2. 实现功能

按照分层架构实现：
- Domain 层：定义模型和规则
- Application 层：实现用例
- Infrastructure 层：实现基础设施
- Interfaces 层：暴露 API

#### 3. 添加测试

在 `tests/` 目录下添加测试文件。

#### 4. 更新文档

更新相关文档和用户手册。

---

## 相关资源

### 文档

- [用户手册](USER_GUIDE.md) - 完整的使用指南
- [架构文档](docs/architecture.md) - 系统架构规范
- [设计系统](docs/design-system.md) - UI/UX 设计规范
- [UI/UX 工作流](docs/ui-ux-workflow.md) - 前端开发流程

### API 文档

- [交互式文档](http://localhost:8000/docs) - Swagger UI
- [ReDoc 文档](http://localhost:8000/redoc) - ReDoc UI

### 外部资源

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Qdrant 文档](https://qdrant.tech/documentation/)
- [DeepSeek API](https://platform.deepseek.com/api-docs/)
- [Sentence Transformers](https://www.sbert.net/)

---

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 联系方式

- **问题反馈**：[GitHub Issues](https://github.com/your-repo/issues)
- **功能建议**：[GitHub Discussions](https://github.com/your-repo/discussions)

---

**版本**：0.1.0  
**最后更新**：2025-01-17  
**维护者**：AI Tech Pioneer Team
