# Requirements: RAG System

## Overview

构建一个基于检索增强生成（RAG）的文档问答系统，支持文档上传、智能分块、向量存储和语义检索，并提供 Web 界面进行文档和 Chunk 管理。

## User Stories

### US-1: Document Upload
**As a** 用户  
**I want to** 通过 Web 界面上传文档  
**So that** 系统能够处理和存储文档内容用于后续检索

**Acceptance Criteria:**
- 支持上传常见文档格式（PDF、TXT、MD、DOCX）
- 文档上传后自动进行分块处理
- 分块后的内容自动生成向量嵌入并存储到 Qdrant
- 上传进度显示和错误处理
- 文档元数据记录（文件名、上传时间、大小、类型）

### US-2: Chunk Management - View
**As a** 用户  
**I want to** 查看文档的所有 Chunk  
**So that** 我能够了解文档的分块情况和内容

**Acceptance Criteria:**
- 以列表形式展示文档的所有 Chunk
- 显示 Chunk 的基本信息（ID、内容预览、状态、创建时间）
- 支持按文档、状态、时间筛选和排序
- 分页显示大量 Chunk

### US-3: Chunk Management - Edit Status
**As a** 用户  
**I want to** 标记 Chunk 为 deprecated 或 inactive  
**So that** 我能够控制哪些 Chunk 参与检索

**Acceptance Criteria:**
- 支持将 Chunk 状态从 active 改为 deprecated
- 支持将 Chunk 状态从 active 改为 inactive，并提供删除原因（如：low_answerability）
- 支持永久删除 Chunk
- 状态变更实时生效
- 提供 Undo 操作（可选）
- 记录状态变更历史和版本号

### US-4: Chunk Management - Merge
**As a** 用户  
**I want to** 合并相邻的 Chunk  
**So that** 我能够优化 Chunk 的语义完整性

**Acceptance Criteria:**
- 支持将一个 Chunk 与前一个或后一个 Chunk 合并
- 合并后重新生成向量嵌入
- 自动更新相关元数据
- 合并操作可撤销（可选）

### US-5: Semantic Search
**As a** 用户  
**I want to** 输入问题并获得基于文档的答案  
**So that** 我能够快速获取相关信息

**Acceptance Criteria:**
- 支持自然语言问题输入
- 仅检索 active 状态的 Chunk
- 使用 DeepSeek LLM 生成答案
- 显示参考的 Chunk 来源
- 支持相关性评分展示

### US-6: Chunking Strategy
**As a** 系统  
**I want to** 使用 Parent-Child Chunking 混合策略  
**So that** 提高检索的准确性和上下文完整性

**Acceptance Criteria:**
- 默认使用 Parent-Child Chunking（父-子分块）混合策略
- Parent Chunk：较大的语义单元（1500-2000 tokens），用于提供完整上下文
- Child Chunk：较小的检索单元（500-800 tokens），用于精确匹配
- Child Chunk 重叠：50-100 tokens
- 在自然边界（段落、句子）分割
- 所有 Chunk 默认状态为 active
- 检索时返回 Child Chunk，但关联其 Parent Chunk 以提供完整上下文

### US-7: Embedding Generation
**As a** 系统  
**I want to** 为每个 Chunk 生成向量嵌入  
**So that** 能够进行语义相似度检索

**Acceptance Criteria:**
- 使用 bge-base-zh-v1.5 Embedding 模型（中文优化）
- 向量维度：768 维
- 支持批量嵌入生成以提高性能
- 嵌入结果与 Chunk 一起存储
- 支持中英文混合文本嵌入

### US-8: Vector Storage
**As a** 系统  
**I want to** 使用 Qdrant 存储向量数据  
**So that** 实现高效的相似度检索

**Acceptance Criteria:**
- 使用本地部署的 Qdrant（http://localhost:6333）
- 为每个文档创建独立的 Collection
- 存储向量、Chunk 内容和元数据
- 支持基于余弦相似度的检索

## Functional Requirements

### FR-1: Document Processing
- 支持解析 PDF、TXT、MD、DOCX 格式
- 提取文档文本内容
- 保留文档结构信息（标题、段落等）
- 记录文档元数据

### FR-2: Chunking
- 实现 Parent-Child Chunking 混合算法
- Parent Chunk 配置：chunk_size=1750, chunk_overlap=0
- Child Chunk 配置：chunk_size=650, chunk_overlap=50
- 在段落、句子等自然边界分割
- 为每个 Chunk 生成唯一 ID
- 维护 Parent-Child 关联关系

### FR-3: Embedding
- 使用 bge-base-zh-v1.5 模型（BAAI/bge-base-zh-v1.5）
- 生成 768 维向量
- 批量处理以提高效率
- 缓存嵌入结果
- 支持中英文混合文本

### FR-4: Vector Storage
- 集成 Qdrant 客户端（版本 >=1.16.0）
- 创建和管理 Collections
- 存储向量和元数据
- 实现相似度搜索

### FR-5: LLM Integration
- 集成 DeepSeek API
- 构建 RAG prompt 模板
- 处理 API 请求和响应
- 错误处理和重试机制

### FR-6: Chunk State Management
- Chunk 状态：active, deprecated, inactive
- 默认状态：active
- 状态过滤：仅检索 active Chunk
- 状态变更操作：支持 deprecated 和 inactive 状态
- inactive 状态需要提供删除原因（如：low_answerability）
- Chunk 质量标记：high, repaired, suspect
- Chunk 版本管理：每次状态变更或内容更新时版本号递增

### FR-7: Web API
- RESTful API 设计
- 文档上传端点
- Chunk 查询和管理端点
- 问答端点
- 错误处理和验证

### FR-8: Web UI
- 使用 ui-ux-pro-max-skill 框架提供设计智能
- 参考文档：https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- 响应式设计
- 文档上传界面
- Chunk 管理界面（查看、编辑、合并）
- 问答界面
- 支持多种 UI 风格和配色方案

## Non-Functional Requirements

### NFR-1: Performance
- 文档上传处理时间 < 10s（1MB 文件）
- 检索响应时间 < 2s
- 支持并发上传和查询
- 向量检索延迟 < 500ms

### NFR-2: Scalability
- 支持存储 1000+ 文档
- 支持 10,000+ Chunk
- 支持多用户并发访问
- 数据库连接池管理

### NFR-3: Reliability
- 系统可用性 > 99%
- 数据持久化保证
- 错误恢复机制
- 日志记录和监控

### NFR-4: Usability
- 直观的用户界面
- 清晰的操作反馈
- 帮助文档和提示
- 错误信息友好

### NFR-5: Security
- 输入验证和清理
- API 密钥保护
- 文件上传限制
- 访问控制（未来扩展）

## Data Requirements

### DR-1: Chunk Metadata Structure
```python
{
    "chunk_id": str,           # 唯一标识符
    "document_id": str,        # 所属文档 ID
    "parent_chunk_id": Optional[str],  # 父 Chunk ID（Child Chunk 关联）
    "content": str,            # Chunk 文本内容
    "status": str,             # "active | deprecated | inactive"
    "inactive_reason": Optional[str],  # 如：low_answerability (仅当 status 为 inactive 时)
    "quality": str,            # "high | repaired | suspect"
    "version": int,            # 版本号，从 1 开始
    "chunk_type": str,         # "parent | child"
    "chunk_index": int,        # 在文档中的顺序
    "start_char": int,         # 在原文档中的起始位置
    "end_char": int,           # 在原文档中的结束位置
    "embedding": List[float],   # 向量嵌入
    "created_at": datetime,    # 创建时间
    "updated_at": datetime,    # 更新时间
    "metadata": {              # 额外元数据
        "source_file": str,    # 源文件名
        "file_type": str,      # 文件类型
        "page_number": Optional[int],  # 页码（PDF）
        "section_title": Optional[str], # 所属章节
        "word_count": int,     # 字数
        "token_count": int     # Token 数
    }
}
```

### DR-2: Document Metadata Structure
```python
{
    "document_id": str,        # 唯一标识符
    "filename": str,           # 文件名
    "file_type": str,          # 文件类型
    "file_size": int,          # 文件大小（字节）
    "upload_time": datetime,   # 上传时间
    "total_chunks": int,       # 总 Chunk 数
    "active_chunks": int,      # active Chunk 数
    "status": str,             # "processing", "completed", "error"
    "error_message": Optional[str],  # 错误信息
    "metadata": {              # 额外元数据
        "title": Optional[str],       # 文档标题
        "author": Optional[str],      # 作者
        "created_date": Optional[datetime],  # 创建日期
        "page_count": Optional[int]   # 页数
    }
}
```

## Constraints

### C-1: Technology Stack
- 后端：Python 3.12+
- 向量数据库：Qdrant 1.16.3（本地部署）
- LLM：DeepSeek API
- Embedding 模型：bge-base-zh-v1.5（768维）
- 前端：ui-ux-pro-max-skill（设计智能）
- Web 框架：FastAPI（推荐）

### C-2: Architecture
- 遵循分层架构（domain/application/infrastructure/interfaces）
- Spec-driven 开发模式
- 严格的架构边界

### C-3: Deployment
- 本地开发环境
- Qdrant 本地实例（http://localhost:6333）
- 环境变量配置

## Assumptions

### A-1: User Expertise
- 用户具备基本的计算机操作能力
- 用户了解如何上传和管理文档

### A-2: Document Types
- 主要处理文本类文档
- PDF 文档包含可提取的文本
- 文档语言主要为中文和英文

### A-3: Network
- 本地网络稳定
- DeepSeek API 可访问
- Qdrant 服务正常运行

## Dependencies

### D-1: External Services
- Qdrant（本地部署）
- DeepSeek API
- Embedding 模型下载

### D-2: Python Libraries
- qdrant-client >= 1.16.0
- sentence-transformers
- fastapi
- uvicorn
- python-multipart
- pydantic
- python-dotenv

## Open Questions

### OQ-1: DeepSeek API Configuration
**问题**: DeepSeek API 的具体配置方式和密钥管理？

**解决方案**: DeepSeek API Key 通过环境变量配置，使用 Python 标准配置文件（.env）管理

### OQ-2: Frontend Technology Stack
**问题**: 前端具体使用什么技术栈？（React/Vue/纯HTML+Tailwind）

**解决方案**: 使用 React 作为前端技术栈，结合 ui-ux-pro-max-skill 提供的设计指导

## Out of Scope

- 用户认证和授权
- 多租户支持
- 文档版本控制
- 实时协作
- 高级 RAG 技术（如重排序、查询扩展）
- 多模态文档（图片、表格）
- 导出功能
- 分析和统计
