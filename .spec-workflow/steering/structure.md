# Codebase Structure

## Directory Organization

```
aitechpioneer/
├── .spec-workflow/          # Spec-workflow 配置和文档
│   ├── steering/            # 项目级指导文档
│   │   ├── product.md       # 产品愿景和目标
│   │   ├── tech.md          # 技术架构决策
│   │   └── structure.md     # 代码库结构（本文件）
│   └── specs/               # 功能规格说明
│       └── {spec-name}/     # 单个功能的完整规格
│           ├── requirements.md
│           ├── design.md
│           ├── tasks.md
│           └── Implementation Logs/
│
├── spec/                    # 系统规格说明（唯一事实源）
│   ├── system.spec.md       # 系统级规约
│   ├── layers/              # 层级规约
│   │   ├── domain.spec.md
│   │   ├── application.spec.md
│   │   ├── infrastructure.spec.md
│   │   └── interfaces.spec.md
│   └── modules/             # 模块规约
│       └── document_processing.spec.md
│
├── src/                     # 源代码
│   └── aitechpioneer/       # 主包
│       ├── domain/          # 业务模型和规则
│       │   ├── models.py
│       │   ├── services.py
│       │   └── ports.py
│       ├── application/     # 用例编排
│       │   └── use_cases.py
│       ├── infrastructure/  # 基础设施实现
│       │   ├── db.py
│       │   ├── cache.py
│       │   └── llm.py
│       ├── interfaces/      # 对外接口
│       │   ├── api.py
│       │   └── cli.py
│       └── settings.py      # 配置管理
│
├── scripts/                 # 工具脚本
│   ├── validate_spec.py     # Spec 验证脚本
│   └── validate_structure.py # 结构验证脚本
│
├── docs/                    # 项目文档
│   ├── architecture.md      # 架构说明
│   └── conventions.md       # 编码约定
│
├── AGENT.md                 # Agent 行为规约（最高优先级）
├── README.md                # 项目说明
└── pyproject.toml           # 项目配置
```

## File Placement Rules

### Domain Layer (`src/aitechpioneer/domain/`)
- **models.py**：业务模型和数据结构
- **services.py**：业务逻辑和领域服务
- **ports.py**：接口定义（供 infrastructure 实现）

**Rules**：
- 只能使用 Python 标准库
- 不能依赖其他层
- 不包含 IO、网络、数据库操作

### Application Layer (`src/aitechpioneer/application/`)
- **use_cases.py**：用例编排和流程控制

**Rules**：
- 只能依赖 domain 层
- 不能直接访问数据库
- 不能直接调用第三方 API
- 通过接口调用 infrastructure

### Infrastructure Layer (`src/aitechpioneer/infrastructure/`)
- **db.py**：数据库访问和操作
- **cache.py**：缓存实现
- **llm.py**：LLM 服务集成

**Rules**：
- 可以依赖 domain 和 application
- 实现定义的接口
- 处理所有 IO、网络、数据库操作

### Interfaces Layer (`src/aitechpioneer/interfaces/`)
- **api.py**：HTTP API 端点
- **cli.py**：命令行接口

**Rules**：
- 只能依赖 application 层
- 只做参数解析和调用
- 不实现业务规则

## Coding Patterns

### Import Rules
```python
# ✅ 正确的导入
from domain.models import Model
from domain.ports import Port
from application.use_cases import UseCase

# ❌ 错误的导入（跨层反向依赖）
from infrastructure.db import Database  # 在 domain 层
from interfaces.api import API          # 在 application 层
```

### Naming Conventions
- **Classes**：PascalCase（如 `DocumentProcessor`）
- **Functions/Methods**：snake_case（如 `process_document`）
- **Constants**：UPPER_SNAKE_CASE（如 `MAX_RETRIES`）
- **Private Members**：前缀下划线（如 `_internal_method`）

### File Organization
- **Single Responsibility**：每个文件只有一个明确的职责
- **Clear Naming**：文件名应清晰反映其内容
- **Minimal Dependencies**：尽量减少文件间的依赖
- **Explicit Boundaries**：清晰的层级边界

## Module Structure

### Module Spec Format
每个模块在 `spec/modules/` 下有一个 `.spec.md` 文件：

```markdown
# Module Name Specification

## Responsibility
模块的职责描述

## Scope
模块影响的文件和目录

## Allowed Files
允许创建/修改的文件列表

## Forbidden
禁止的行为和依赖

## Dependencies
模块的依赖关系

## Notes
额外的说明和注意事项
```

### Layer Spec Format
每个层级在 `spec/layers/` 下有一个 `.spec.md` 文件：

```markdown
# Layer Name Specification

## Responsibility
层级的职责描述

## Scope
层级影响的目录

## Allowed Files
允许的文件类型

## Forbidden
禁止的行为

## Dependencies
允许的依赖

## Notes
额外的说明
```

## Validation Rules

### Spec Coverage
- 所有 public 符号必须在 spec 中声明
- 未声明的符号会被标记为警告
- 缺失的实现会导致验证失败

### Layer Boundaries
- 禁止跨层反向依赖
- 禁止 domain 层访问 infrastructure
- 禁止 application 层直接访问数据库

### Structure Validation
- 所有 spec 声明的目录必须存在
- 不允许在 spec 外创建新目录
- 不允许在未修改 spec 的情况下新增文件

## Development Workflow

### 1. Spec Creation
1. 在 `spec/modules/` 创建新的 `.spec.md` 文件
2. 定义模块的职责、范围、依赖
3. 更新相关的 layer specs（如需要）

### 2. Implementation
1. 读取 AGENT.md 了解行为规约
2. 加载 system.spec.md 和 layer specs
3. 加载目标 module spec
4. 实现最小必要代码
5. 运行验证脚本

### 3. Validation
```bash
# 验证 spec 覆盖率
python scripts/validate_spec.py

# 验证目录结构
python scripts/validate_structure.py
```

### 4. Completion
- 所有验证通过
- 所有 spec 项已实现
- 无未声明的代码
- 无架构违规

## Documentation Standards

### Spec Documents
- 使用 Markdown 格式
- 清晰的章节结构
- 明确的职责和边界
- 具体的示例（如需要）

### Code Comments
- 遵循 PEP 257
- 解释"为什么"而非"是什么"
- 保持简洁和准确
- 避免显而易见的注释

### README Files
- 项目概述
- 快速开始
- 架构说明
- 开发指南

## Testing Strategy

### Unit Tests
- 测试 domain 层的业务逻辑
- 使用 mock 隔离依赖
- 覆盖所有边界情况

### Integration Tests
- 测试跨层交互
- 测试用例编排
- 测试基础设施集成

### Validation Tests
- 运行 validate_spec.py
- 运行 validate_structure.py
- 检查架构合规性

## Git Workflow

### Branch Strategy
- `main`：稳定版本
- `feature/*`：功能开发
- `fix/*`：错误修复

### Commit Messages
- 使用约定式提交
- 引用相关的 spec 文件
- 描述变更的影响

### Code Review
- 检查 spec 合规性
- 检查架构边界
- 运行验证脚本
