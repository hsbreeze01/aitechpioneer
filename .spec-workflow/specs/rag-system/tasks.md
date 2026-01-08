# Tasks: RAG System

## Task Overview

本文档将 RAG 系统的实现分解为可执行的任务，按照优先级和依赖关系组织。每个任务都有明确的验收标准和依赖关系。

## Task Legend

- `[ ]` - 待开始 (Pending)
- `[-]` - 进行中 (In Progress)
- `[x]` - 已完成 (Completed)

## Phase 1: Infrastructure Setup

### Task 1.1: Update Project Dependencies

**Priority**: High  
**Status**: [ ]  
**Estimated Time**: 30 minutes

**Description**: 更新 pyproject.toml 以包含 RAG 系统所需的所有依赖项

**Dependencies**: None

**Acceptance Criteria**:
- [ ] pyproject.toml 包含所有必需的依赖项
- [ ] 依赖版本经过验证且兼容
- [ ] 包含开发依赖项（测试、linting、格式化）

**Implementation Steps**:
1. 更新 pyproject.toml 的 dependencies 部分
2. 添加可选的开发依赖项
3. 验证依赖项版本兼容性
4. 运行 `pip install -e .` 安装依赖

**Files to Modify**:
- [pyproject.toml](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/pyproject.toml)

---

### Task 1.2: Update Environment Configuration

**Priority**: High  
**Status**: [ ]  
**Estimated Time**: 15 minutes

**Description**: 更新 .env.example 文件以包含 RAG 系统所需的环境变量

**Dependencies**: Task 1.1

**Acceptance Criteria**:
- [ ] .env.example 包含所有必需的环境变量
- [ ] 每个变量都有清晰的注释说明
- [ ] 包含 DeepSeek API 密钥配置

**Implementation Steps**:
1. 添加 DEEPSEEK_API_KEY 环境变量
2. 添加其他必要的配置项
3. 为每个变量添加详细注释

**Files to Modify**:
- [.env.example](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/.env.example)

---

### Task 1.3: Update Settings Module

**Priority**: High  
**Status**: [ ]  
**Estimated Time**: 15 minutes

**Description**: 更新 settings.py 以支持新的环境变量

**Dependencies**: Task 1.2

**Acceptance Criteria**:
- [ ] Settings 类包含所有新的配置项
- [ ] 使用 pydantic-settings 进行配置管理
- [ ] 提供合理的默认值

**Implementation Steps**:
1. 添加 deepseek_api_key 配置项
2. 添加其他必要的配置项
3. 验证配置加载逻辑

**Files to Modify**:
- [src/aitechpioneer/settings.py](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/src/aitechpioneer/settings.py)

---

## Phase 2: Domain Layer

### Task 2.1: Create Domain Models

**Priority**: High  
**Status**: [ ]  
**Estimated Time**: 45 minutes

**Description**: 创建 Document 和 Chunk 领域模型，包括枚举类型和数据类

**Dependencies**: Task 1.3

**Acceptance Criteria**:
- [ ] Document 模型包含所有必需字段
- [ ] Chunk 模型包含所有必需字段
- [ ] 所有枚举类型正确定义
- [ ] 模型包含必要的工厂方法和业务逻辑

**Implementation Steps**:
1. 创建 DocumentStatus, FileType 枚举
2. 创建 DocumentMetadata 和 Document 数据类
3. 创建 ChunkStatus, ChunkQuality, ChunkType 枚举
4. 创建 ChunkMetadata 和 Chunk 数据类
5. 实现工厂方法（create）
6. 实现业务方法（update_status, update_quality）

**Files to Create**:
- [src/aitechpioneer/domain/models.py](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/src/aitechpioneer/domain/models.py)

---

### Task 2.2: Create Domain Ports

**Priority**: High  
**Status**: [ ]  
**Estimated Time**: 30 minutes

**Description**: 创建领域端口接口，定义向量数据库、嵌入服务和 LLM 服务的抽象接口

**Dependencies**: Task 2.1

**Acceptance Criteria**:
- [ ] VectorDatabasePort 定义所有必需的方法
- [ ] EmbeddingServicePort 定义所有必需的方法
- [ ] LLMServicePort 定义所有必需的方法
- [ ] 所有方法都有清晰的类型注解

**Implementation Steps**:
1. 创建 VectorDatabasePort 抽象类
2. 创建 EmbeddingServicePort 抽象类
3. 创建 LLMServicePort 抽象类
4. 为所有方法添加类型注解和文档字符串

**Files to Modify**:
- [src/aitechpioneer/domain/ports.py](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/src/aitechpioneer/domain/ports.py)

---

### Task 2.3: Create Domain Services

**Priority**: Medium  
**Status**: [ ]  
**Estimated Time**: 30 minutes

**Description**: 创建领域服务，封装复杂的业务逻辑

**Dependencies**: Task 2.1, Task 2.2

**Acceptance Criteria**:
- [ ] EmbeddingService 封装嵌入生成逻辑
- [ ] 服务层保持无状态
- [ ] 服务可被应用层复用

**Implementation Steps**:
1. 创建 EmbeddingService 领域服务
2. 实现嵌入生成和批处理逻辑
3. 添加必要的验证和错误处理

**Files to Modify**:
- [src/aitechpioneer/domain/services.py](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/src/aitechpioneer/domain/services.py)

---

## Phase 3: Infrastructure Layer

### Task 3.1: Implement BGE Embedding Service

**Priority**: High  
**Status**: [ ]  
**Estimated Time**: 45 minutes

**Description**: 实现 BGE 嵌入服务，使用 sentence-transformers 库

**Dependencies**: Task 2.2, Task 2.3

**Acceptance Criteria**:
- [ ] 使用 BAAI/bge-base-zh-v1.5 模型
- [ ] 支持单个文本和批量文本嵌入生成
- [ ] 返回 768 维向量
- [ ] 实现向量归一化

**Implementation Steps**:
1. 创建 BGEEmbeddingService 类
2. 实现 EmbeddingServicePort 接口
3. 初始化 sentence-transformers 模型
4. 实现单个文本嵌入生成
5. 实现批量文本嵌入生成
6. 添加模型缓存机制

**Files to Create**:
- [src/aitechpioneer/infrastructure/embedding.py](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/src/aitechpioneer/infrastructure/embedding.py)

---

### Task 3.2: Implement Qdrant Vector Database

**Priority**: High  
**Status**: [ ]  
**Estimated Time**: 60 minutes

**Description**: 实现 Qdrant 向量数据库集成，支持集合管理和向量操作

**Dependencies**: Task 2.2

**Acceptance Criteria**:
- [ ] 连接到本地 Qdrant 实例
- [ ] 支持集合创建和检查
- [ ] 支持向量插入和更新
- [ ] 支持向量检索和过滤
- [ ] 支持向量删除
- [ ] 正确处理 Chunk 和 Payload 的转换

**Implementation Steps**:
1. 创建 QdrantVectorDatabase 类
2. 实现 VectorDatabasePort 接口
3. 实现集合管理方法
4. 实现向量插入方法
5. 实现向量检索方法（支持状态过滤）
6. 实现向量更新方法
7. 实现向量删除方法
8. 实现 Chunk 和 Payload 转换方法

**Files to Create**:
- [src/aitechpioneer/infrastructure/qdrant_db.py](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/src/aitechpioneer/infrastructure/qdrant_db.py)

---

### Task 3.3: Implement Parent-Child Chunking Service

**Priority**: High  
**Status**: [ ]  
**Estimated Time**: 45 minutes

**Description**: 实现 Parent-Child 混合分块策略

**Dependencies**: Task 2.1

**Acceptance Criteria**:
- [ ] Parent Chunk 大小为 1500-2000 tokens
- [ ] Child Chunk 大小为 500-800 tokens
- [ ] Child Chunk 重叠 50-100 tokens
- [ ] 在自然边界（段落、句子）分割
- [ ] 返回 Parent 和 Child Chunk 列表

**Implementation Steps**:
1. 创建 ChunkConfig 数据类
2. 创建 ParentChildChunker 类
3. 实现 Parent Chunk 创建逻辑
4. 实现 Child Chunk 创建逻辑
5. 实现自然边界查找逻辑
6. 添加配置参数支持

**Files to Create**:
- [src/aitechpioneer/infrastructure/chunking.py](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/src/aitechpioneer/infrastructure/chunking.py)

---

### Task 3.4: Implement Document Parser

**Priority**: High  
**Status**: [ ]  
**Estimated Time**: 45 minutes

**Description**: 实现文档解析服务，支持多种文档格式

**Dependencies**: Task 2.1

**Acceptance Criteria**:
- [ ] 支持 PDF 文档解析
- [ ] 支持 TXT 文档解析
- [ ] 支持 Markdown 文档解析
- [ ] 支持 DOCX 文档解析
- [ ] 提取文档元数据（标题、作者、页数等）
- [ ] 返回纯文本内容

**Implementation Steps**:
1. 创建 DocumentParser 类
2. 实现 PDF 解析逻辑（使用 pypdf）
3. 实现 TXT 解析逻辑
4. 实现 Markdown 解析逻辑
5. 实现 DOCX 解析逻辑（使用 python-docx）
6. 实现元数据提取逻辑
7. 添加错误处理和日志记录

**Files to Create**:
- [src/aitechpioneer/infrastructure/document_parser.py](file:////Users/lancer.zhang/ProjectNIO/aitechpioneer/src/aitechpioneer/infrastructure/document_parser.py)

---

### Task 3.5: Implement DeepSeek LLM Service

**Priority**: High  
**Status**: [ ]  
**Estimated Time**: 45 minutes

**Description**: 实现 DeepSeek LLM 服务集成

**Dependencies**: Task 2.2

**Acceptance Criteria**:
- [ ] 连接到 DeepSeek API
- [ ] 支持生成答案
- [ ] 支持带来源的答案生成
- [ ] 正确处理 API 错误
- [ ] 支持重试机制

**Implementation Steps**:
1. 创建 DeepSeekLLMService 类
2. 实现 LLMServicePort 接口
3. 实现 API 调用方法
4. 实现答案生成方法
5. 实现带来源的答案生成方法
6. 添加错误处理和重试逻辑

**Files to Create**:
- [src/aitechpioneer/infrastructure/deepseek_llm.py](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/src/aitechpioneer/infrastructure/deepseek_llm.py)

---

## Phase 4: Application Layer

### Task 4.1: Implement Document Upload Use Case

**Priority**: High  
**Status**: [ ]  
**Estimated Time**: 60 minutes

**Description**: 实现文档上传用例，编排文档处理的完整流程

**Dependencies**: Task 3.1, Task 3.2, Task 3.3, Task 3.4

**Acceptance Criteria**:
- [ ] 解析文档内容
- [ ] 使用 Parent-Child 策略分块
- [ ] 生成所有 Chunk 的嵌入
- [ ] 创建 Qdrant 集合
- [ ] 存储所有 Chunk 到向量数据库
- [ ] 更新文档状态为 completed
- [ ] 正确处理错误情况

**Implementation Steps**:
1. 创建 DocumentUploadUseCase 类
2. 实现 execute 方法
3. 调用 DocumentParser 解析文档
4. 调用 ParentChildChunker 分块
5. 调用 BGEEmbeddingService 生成嵌入
6. 调用 QdrantVectorDatabase 存储数据
7. 更新文档状态
8. 添加错误处理和日志记录

**Files to Modify**:
- [src/aitechpioneer/application/use_cases.py](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/src/aitechpioneer/application/use_cases.py)

---

### Task 4.2: Implement Chunk Manager Use Case

**Priority**: High  
**Status**: [ ]  
**Estimated Time**: 45 minutes

**Description**: 实现 Chunk 管理用例，支持状态更新、合并和删除操作

**Dependencies**: Task 3.2, Task 2.1

**Acceptance Criteria**:
- [ ] 支持更新 Chunk 状态
- [ ] 支持合并两个 Chunk
- [ ] 支持删除 Chunk
- [ ] 正确处理版本控制
- [ ] 更新向量数据库

**Implementation Steps**:
1. 创建 ChunkManagerUseCase 类
2. 实现 update_chunk_status 方法
3. 实现 merge_chunks 方法
4. 实现 delete_chunk 方法
5. 添加必要的验证逻辑
6. 添加错误处理

**Files to Modify**:
- [src/aitechpioneer/application/use_cases.py](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/src/aitechpioneer/application/use_cases.py)

---

### Task 4.3: Implement RAG Use Case

**Priority**: High  
**Status**: [ ]  
**Estimated Time**: 45 minutes

**Description**: 实现 RAG 用例，支持问答功能

**Dependencies**: Task 3.1, Task 3.2, Task 3.5

**Acceptance Criteria**:
- [ ] 生成问题嵌入
- [ ] 检索相关 Chunk（仅 active 状态）
- [ ] 调用 LLM 生成答案
- [ ] 返回答案和来源 Chunk
- [ ] 支持自定义检索参数

**Implementation Steps**:
1. 创建 RAGUseCase 类
2. 实现 answer_question 方法
3. 调用 BGEEmbeddingService 生成问题嵌入
4. 调用 QdrantVectorDatabase 检索相关 Chunk
5. 调用 DeepSeekLLMService 生成答案
6. 返回答案和来源
7. 添加错误处理

**Files to Modify**:
- [src/aitechpioneer/application/use_cases.py](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/src/aitechpioneer/application/use_cases.py)

---

## Phase 5: Interfaces Layer

### Task 5.1: Implement Web API

**Priority**: High  
**Status**: [ ]  
**Estimated Time**: 90 minutes

**Description**: 实现 FastAPI Web API，提供 RESTful 端点

**Dependencies**: Task 4.1, Task 4.2, Task 4.3

**Acceptance Criteria**:
- [ ] POST /api/documents/upload - 上传文档
- [ ] GET /api/documents/{document_id}/chunks - 获取文档的 Chunk 列表
- [ ] PUT /api/chunks/{chunk_id}/status - 更新 Chunk 状态
- [ ] POST /api/chunks/merge - 合并两个 Chunk
- [ ] DELETE /api/chunks/{chunk_id} - 删除 Chunk
- [ ] POST /api/questions/answer - 提问并获取答案
- [ ] 所有端点有适当的输入验证
- [ ] 所有端点有错误处理
- [ ] API 文档自动生成

**Implementation Steps**:
1. 创建 FastAPI 应用实例
2. 创建 Pydantic 模型用于请求/响应
3. 实现文档上传端点
4. 实现 Chunk 列表端点
5. 实现 Chunk 状态更新端点
6. 实现 Chunk 合并端点
7. 实现 Chunk 删除端点
8. 实现问答端点
9. 添加 CORS 中间件
10. 添加错误处理中间件

**Files to Modify**:
- [src/aitechpioneer/interfaces/api.py](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/src/aitechpioneer/interfaces/api.py)

---

### Task 5.2: Implement Web UI

**Priority**: Medium  
**Status**: [ ]  
**Estimated Time**: 180 minutes

**Description**: 实现 Web UI，基于 ui-ux-pro-max-skill 设计指导

**Dependencies**: Task 5.1

**Acceptance Criteria**:
- [ ] 文档上传界面
- [ ] Chunk 列表和详情视图
- [ ] Chunk 状态管理界面
- [ ] Chunk 合并界面
- [ ] 问答界面
- [ ] 响应式设计
- [ ] 良好的用户体验

**Implementation Steps**:
1. 使用 React + Tailwind CSS 技术栈
2. 创建 React 项目结构
3. 实现文档上传组件
4. 实现 Chunk 列表组件
5. 实现 Chunk 详情组件
6. 实现 Chunk 状态管理组件
7. 实现 Chunk 合并组件
8. 实现问答组件
9. 添加路由和导航
10. 应用 ui-ux-pro-max-skill 设计原则

**Files to Create**:
- frontend/ 目录（React + Tailwind CSS）

---

## Phase 6: Testing

### Task 6.1: Write Unit Tests

**Priority**: Medium  
**Status**: [ ]  
**Estimated Time**: 120 minutes

**Description**: 为 Domain 和 Application 层编写单元测试

**Dependencies**: Task 2.3, Task 4.3

**Acceptance Criteria**:
- [ ] Domain 模型测试覆盖率 > 80%
- [ ] Application 用例测试覆盖率 > 80%
- [ ] 所有测试通过
- [ ] 使用 mock 隔离依赖

**Implementation Steps**:
1. 创建测试目录结构
2. 编写 Domain 模型测试
3. 编写 Application 用例测试
4. 添加 mock 和 fixture
5. 运行测试并验证覆盖率

**Files to Create**:
- tests/unit/domain/
- tests/unit/application/

---

### Task 6.2: Write Integration Tests

**Priority**: Medium  
**Status**: [ ]  
**Estimated Time**: 90 minutes

**Description**: 编写集成测试，测试完整的业务流程

**Dependencies**: Task 5.1

**Acceptance Criteria**:
- [ ] 文档上传流程测试
- [ ] Chunk 管理流程测试
- [ ] 问答流程测试
- [ ] 所有测试通过
- [ ] 使用测试数据库

**Implementation Steps**:
1. 创建集成测试目录
2. 编写文档上传集成测试
3. 编写 Chunk 管理集成测试
4. 编写问答集成测试
5. 添加测试数据清理逻辑

**Files to Create**:
- tests/integration/

---

### Task 6.3: Write API Tests

**Priority**: Medium  
**Status**: [ ]  
**Estimated Time**: 60 minutes

**Description**: 编写 API 端点测试

**Dependencies**: Task 5.1

**Acceptance Criteria**:
- [ ] 所有 API 端点测试通过
- [ ] 测试各种输入场景
- [ ] 测试错误处理

**Implementation Steps**:
1. 创建 API 测试目录
2. 编写文档上传 API 测试
3. 编写 Chunk 管理 API 测试
4. 编写问答 API 测试

**Files to Create**:
- tests/api/

---

## Phase 7: Documentation & Deployment

### Task 7.1: Write README

**Priority**: Low  
**Status**: [ ]  
**Estimated Time**: 30 minutes

**Description**: 编写项目 README 文档

**Dependencies**: Task 5.2

**Acceptance Criteria**:
- [ ] 项目介绍
- [ ] 功能特性
- [ ] 安装说明
- [ ] 使用说明
- [ ] 配置说明
- [ ] API 文档链接

**Implementation Steps**:
1. 创建 README.md
2. 添加项目介绍
3. 添加功能特性列表
4. 添加安装步骤
5. 添加使用示例
6. 添加配置说明

**Files to Create**:
- [README.md](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/README.md)

---

### Task 7.2: Create Docker Configuration

**Priority**: Low  
**Status**: [ ]  
**Estimated Time**: 45 minutes

**Description**: 创建 Docker 配置文件，支持容器化部署

**Dependencies**: Task 5.2

**Acceptance Criteria**:
- [ ] Dockerfile 用于后端
- [ ] Dockerfile 用于前端（React）
- [ ] docker-compose.yml 用于本地开发
- [ ] 支持一键启动所有服务

**Implementation Steps**:
1. 创建后端 Dockerfile
2. 创建前端 Dockerfile（React）
3. 创建 docker-compose.yml
4. 添加 Qdrant 服务
5. 添加环境变量配置

**Files to Create**:
- [Dockerfile](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/Dockerfile)
- [docker-compose.yml](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/docker-compose.yml)

---

### Task 7.3: Create Deployment Scripts

**Priority**: Low  
**Status**: [ ]  
**Estimated Time**: 30 minutes

**Description**: 创建部署脚本，简化部署流程

**Dependencies**: Task 7.2

**Acceptance Criteria**:
- [ ] 启动脚本
- [ ] 停止脚本
- [ ] 日志查看脚本
- [ ] 健康检查脚本

**Implementation Steps**:
1. 创建启动脚本
2. 创建停止脚本
3. 创建日志查看脚本
4. 创建健康检查脚本

**Files to Create**:
- scripts/start.sh
- scripts/stop.sh
- scripts/logs.sh
- scripts/health.sh

---

## Task Dependencies Graph

```
Phase 1: Infrastructure Setup
├── Task 1.1: Update Project Dependencies
├── Task 1.2: Update Environment Configuration (depends on 1.1)
└── Task 1.3: Update Settings Module (depends on 1.2)

Phase 2: Domain Layer
├── Task 2.1: Create Domain Models (depends on 1.3)
├── Task 2.2: Create Domain Ports (depends on 2.1)
└── Task 2.3: Create Domain Services (depends on 2.1, 2.2)

Phase 3: Infrastructure Layer
├── Task 3.1: Implement BGE Embedding Service (depends on 2.2, 2.3)
├── Task 3.2: Implement Qdrant Vector Database (depends on 2.2)
├── Task 3.3: Implement Parent-Child Chunking Service (depends on 2.1)
├── Task 3.4: Implement Document Parser (depends on 2.1)
└── Task 3.5: Implement DeepSeek LLM Service (depends on 2.2)

Phase 4: Application Layer
├── Task 4.1: Implement Document Upload Use Case (depends on 3.1, 3.2, 3.3, 3.4)
├── Task 4.2: Implement Chunk Manager Use Case (depends on 3.2, 2.1)
└── Task 4.3: Implement RAG Use Case (depends on 3.1, 3.2, 3.5)

Phase 5: Interfaces Layer
├── Task 5.1: Implement Web API (depends on 4.1, 4.2, 4.3)
└── Task 5.2: Implement Web UI (depends on 5.1)

Phase 6: Testing
├── Task 6.1: Write Unit Tests (depends on 2.3, 4.3)
├── Task 6.2: Write Integration Tests (depends on 5.1)
└── Task 6.3: Write API Tests (depends on 5.1)

Phase 7: Documentation & Deployment
├── Task 7.1: Write README (depends on 5.2)
├── Task 7.2: Create Docker Configuration (depends on 5.2)
└── Task 7.3: Create Deployment Scripts (depends on 7.2)
```

## Progress Tracking

### Completed Tasks
- None

### In Progress Tasks
- None

### Blocked Tasks
- None

### Next Steps
1. Start with Task 1.1: Update Project Dependencies
2. Follow the dependency graph to complete tasks in order
3. Update task status as you complete each task
4. Run tests after each phase to ensure quality

## Notes

- 所有任务都应该遵循项目的代码风格和架构原则
- 每个任务完成后，应该运行 lint 和 typecheck
- 定期提交代码到版本控制系统
- 遇到阻塞问题时，及时更新任务状态并寻求帮助
