# Design: Chunk Optimization Verification

## User Interaction Flow

### Flow 1: 问题发现和分类流程

```
用户提问
  ↓
系统检索 chunks
  ↓
系统生成答案
  ↓
显示答案和参考 chunks
  ↓
自动记录问题历史
  ↓
用户查看答案
  ↓
[用户发现答案不符合预期]
  ↓
用户点击"标记问题"
  ↓
系统弹出问题分类对话框
  ↓
用户填写问题分类信息：
  - 问题类型（事实性/解释性/操作性/对比性）
  - 严重程度（低/中/高/严重）
  - 影响范围（单文档/多文档/全局）
  - 根因（chunk太小/太大/边界不合理/内容不完整）
  ↓
系统自动计算问题优先级
  ↓
系统标记问题状态为"discovered"
  ↓
[可选] 用户关联相关问题
  ↓
[可选] 用户标记相关 chunks
```

### Flow 2: 问题分析和根因分析流程

```
用户进入问题详情页面
  ↓
系统显示问题基本信息
  ↓
用户点击"分析根因"
  ↓
系统基于检索结果分析可能的原因：
  - 检查检索到的 chunks 的相关性评分
  - 检查 chunks 的内容完整性
  - 检查 chunks 的边界是否合理
  - 检查 chunks 之间的关联关系
  ↓
系统显示根因分析结果
  ↓
系统标记问题相关的 chunks
  ↓
系统提供 chunk 优化建议：
  - 合并相邻 chunks
  - 拆分过大的 chunks
  - 调整 chunk 边界
  ↓
用户确认或修正根因分析结果
  ↓
系统更新问题状态为"analyzing"
  ↓
[可选] 用户创建测试计划
```

### Flow 3: Chunk 优化和测试计划创建流程

```
用户进入 chunk 管理页面
  ↓
用户根据根因分析结果进行 chunk 优化：
  - 合并相邻 chunks
  - 拆分过大的 chunks
  - 调整 chunk 边界
  ↓
优化完成后，系统显示"创建测试计划"按钮
  ↓
用户点击"创建测试计划"
  ↓
系统跳转到测试计划创建页面
  ↓
系统自动推荐相关问题：
  - 标记为"discovered"或"analyzing"的问题
  - 与优化 chunks 相关的问题
  - 高优先级的问题
  ↓
用户选择需要验证的问题
  ↓
用户填写测试计划信息：
  - 测试计划名称
  - 描述
  ↓
系统创建测试计划（版本 1）
  ↓
系统记录优化摘要：
  - 执行的优化操作
  - 受影响的文档
  - 受影响的 chunks
  ↓
系统更新相关问题状态为"optimizing"
  ↓
用户点击"执行测试计划"
```

### Flow 4: 测试计划执行和验证流程

```
系统开始执行测试计划
  ↓
系统更新测试计划状态为"running"
  ↓
系统逐个执行问题验证：
  - 使用当前 chunk 状态重新检索
  - 使用当前 chunk 状态重新生成答案
  - 计算答案相似度
  - 计算 chunks 变化
  - 计算评分变化
  - 创建验证记录
  ↓
系统实时显示测试进度
  ↓
所有问题验证完成后
  ↓
系统更新测试计划状态为"completed"
  ↓
系统计算测试结果汇总：
  - 总数、更好、相同、更差、失败
  - 改进率（better / total）
  - 回退率（worse / total）
  ↓
系统生成决策建议：
  - 影响范围分析
  - 风险评估
  - 成本评估
  - 下一步行动建议
  ↓
系统显示测试结果和决策建议
  ↓
用户查看每个问题的详细对比结果
  ↓
用户标记优化效果（更好/相同/更差）
  ↓
[可选] 用户添加评论
  ↓
系统更新相关问题状态为"verifying"
```

### Flow 5: 决策支持和后续行动流程

```
用户查看测试结果和决策建议
  ↓
系统显示决策建议：
  - 继续优化：改进率 > 70%，回退率 < 30%
  - 停止优化：改进率 < 30%，回退率 < 30%
  - 回滚优化：回退率 > 30%
  ↓
系统显示影响范围分析：
  - 受影响的问题数量
  - 受影响的文档数量
  - 受影响的 chunks 数量
  ↓
系统显示风险评估：
  - 风险等级（低/中/高）
  - 可能产生的新问题
  ↓
系统显示成本评估：
  - 剩余问题数量
  - 预估工作量（低/中/高）
  ↓
系统显示下一步行动建议：
  - 继续优化哪些 chunks
  - 如何处理剩余问题
  - 是否需要回滚优化
  ↓
用户做出决策：
  - 继续优化 → 返回 chunk 管理页面
  - 停止优化 → 关闭问题
  - 回滚优化 → 执行回滚操作
  ↓
用户记录决策理由
  ↓
系统记录决策结果
  ↓
系统更新相关问题状态：
  - 继续优化 → "optimizing"
  - 停止优化 → "resolved"
  - 回滚优化 → "analyzing"
```

### Flow 6: 多次验证和趋势分析流程

```
用户进入问题详情页面
  ↓
用户点击"查看验证历史"
  ↓
系统显示所有验证记录
  ↓
用户选择多个验证记录进行对比
  ↓
系统显示对比结果：
  - 答案相似度趋势图
  - 检索相关性评分趋势图
  - Chunks 变化趋势图
  ↓
用户分析优化趋势：
  - 答案质量是否持续改进
  - 检索相关性是否持续提升
  - Chunks 变化是否趋于稳定
  ↓
[可选] 用户导出验证结果对比报告
  ↓
用户基于趋势分析做出决策
```

### Flow 7: 批量验证和汇总流程

```
用户进入问题历史页面
  ↓
用户筛选问题：
  - 按状态筛选（discovered/analyzing/optimizing/verifying）
  - 按严重程度筛选（低/中/高/严重）
  - 按问题类型筛选（事实性/解释性/操作性/对比性）
  - 按优化效果筛选（更好/相同/更差）
  ↓
用户选择多个问题
  ↓
用户点击"批量验证"
  ↓
系统创建批量测试计划
  ↓
系统显示批量测试进度
  ↓
系统逐个执行问题验证
  ↓
测试完成后显示汇总结果：
  - 优化效果分布（更好/相同/更差的问题数量）
  - 问题严重程度分布
  - 问题类型分布
  - 改进率和回退率
  ↓
用户按优化效果和严重程度筛选问题
  ↓
用户批量标记优化效果
  ↓
[可选] 用户导出批量验证结果
  ↓
用户基于汇总结果做出决策
```

### Flow 8: 问题生命周期管理流程

```
问题创建
  ↓
状态：discovered
  ↓
[用户分析根因]
  ↓
状态：analyzing
  ↓
[用户优化 chunks]
  ↓
状态：optimizing
  ↓
[用户执行测试计划]
  ↓
状态：verifying
  ↓
[用户查看决策建议]
  ↓
[用户做出决策]
  ↓
状态：resolved（继续优化 → optimizing，停止优化 → resolved，回滚优化 → analyzing）
  ↓
[用户确认问题已解决]
  ↓
状态：closed
  ↓
[问题生命周期结束]
```

### Flow 9: 用户反馈处理流程

```
用户查看问题答案
  ↓
用户对答案质量进行反馈
  ↓
系统显示反馈选项：
  - 问题已解决
  - 问题未解决
  ↓
用户选择反馈选项
  ↓
[用户选择"问题已解决"]
  ↓
系统更新问题状态为"resolved"
  ↓
系统设置 is_optimization_target = false
  ↓
问题不记录为待优化目标
  ↓
[用户选择"问题未解决"]
  ↓
系统更新问题状态为"discovered"
  ↓
系统设置 is_optimization_target = true
  ↓
系统记录 optimization_target_since = 当前时间
  ↓
问题记录为待分析优化目标
  ↓
系统提示用户进行根因分析
  ↓
用户进入根因分析流程（Flow 2）
```

**重要说明**：
- **仅记录用户反馈"没有解决问题"的问题-答案对作为待分析优化目标**
- **用户反馈"已解决"的问题不记录为待优化目标，直接标记为已解决状态**
- **系统根据用户反馈自动设置 is_optimization_target 标志**
- **待优化目标列表只包含 is_optimization_target = true 的问题**

## System Architecture

### Layer Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Interfaces Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Question     │  │ Test Plan    │  │ Decision     │  │
│  │   API       │  │    API       │  │ Support API  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Verification │  │ Root Cause   │  │ Batch Test   │  │
│  │    API       │  │   API        │  │    API       │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  Application Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Question     │  │ Test Plan    │  │ Decision     │  │
│  │ Management   │  │ Management   │  │ Support     │  │
│  │   Use Case  │  │   Use Case   │  │   Use Case  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Verification │  │ Root Cause   │  │ Batch Test   │  │
│  │   Use Case  │  │   Use Case   │  │   Use Case  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   Domain Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Question     │  │ Test Plan    │  │ Decision     │  │
│  │   Model     │  │   Model      │  │   Service    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Verification │  │ Root Cause   │  │ Priority     │  │
│  │   Model     │  │   Service    │  │ Calculator   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Similarity   │  │ Comparison   │  │ Trend        │  │
│  │   Service    │  │   Service    │  │   Service    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                Infrastructure Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Question     │  │ Test Plan    │  │ Verification │  │
│  │ Repository   │  │ Repository   │  │ Repository   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Component Diagram

```
┌─────────────┐
│   Frontend  │
│  (React)    │
└──────┬──────┘
       │ HTTP API
       ↓
┌──────────────────────────────────────────────────────────┐
│                    FastAPI Server                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Question     │  │ Test Plan    │  │ Decision     │   │
│  │ Controller   │  │ Controller   │  │ Controller   │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                 │           │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐   │
│  │ Question     │  │ Test Plan    │  │ Decision     │   │
│  │ Management   │  │ Management   │  │ Support      │   │
│  │ Use Case    │  │ Use Case    │  │ Use Case     │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                 │           │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐   │
│  │ Question     │  │ Test Plan    │  │ Priority     │   │
│  │ Repository   │  │ Repository   │  │ Calculator   │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                 │           │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐   │
│  │ Verification │  │ Root Cause   │  │ Similarity   │   │
│  │ Use Case    │  │ Service     │  │ Service     │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                 │           │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐   │
│  │ Verification │  │ Comparison   │  │ Trend        │   │
│  │ Repository   │  │ Service     │  │ Service     │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
└─────────┼─────────────────┼─────────────────┼───────────┘
          │                 │                 │
┌─────────▼─────────────────▼─────────────────▼───────────┐
│              External Services                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Qdrant     │  │  DeepSeek    │  │ Sentence-    │  │
│  │  (Vector DB) │  │     API      │  │ Transformers │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└──────────────────────────────────────────────────────────┘
```

## Database Design

### Question History Collection

```python
Collection: question_history

{
    "question_id": str,           # UUID
    "question": str,              # 问题内容
    "answer": str,                # 答案内容
    "retrieved_chunks": [         # 检索到的 chunks
        {
            "chunk_id": str,
            "content": str,
            "score": float,
            "document_id": str
        }
    ],
    "retrieval_params": {
        "top_k": int,
        "score_threshold": float,
        "retrieval_time": float
    },
    "generation_params": {
        "model": str,
        "temperature": float,
        "generation_time": float
    },
    
    # 问题分类
    "classification": {
        "type": str,             # "factual | explanatory | operational | comparative"
        "severity": str,         # "low | medium | high | critical"
        "scope": str,            # "single_document | multi_document | global"
        "root_cause": str,       # "chunk_too_small | chunk_too_large | boundary_issue | incomplete_content | other"
        "priority": int          # 优先级（1-10，自动计算）
    },
    
    # 问题关联
    "related_questions": [str],   # 关联的问题 ID 列表
    "related_chunks": [str],      # 相关的 chunk ID 列表
    
    # 问题状态
    "status": str,               # "discovered | analyzing | optimizing | verifying | resolved | closed"
    "status_history": [          # 状态变更历史
        {
            "status": str,
            "timestamp": datetime,
            "operator": str,
            "comment": Optional[str]
        }
    ],
    
    # 用户反馈
    "user_feedback": {
        "rating": Optional[int],
        "comment": Optional[str],
        "is_helpful": Optional[bool],
        "is_resolved": Optional[bool]  # 用户是否认为问题已解决（true=已解决，false=未解决）
    },
    
    # 待优化目标标记
    # 只有当用户反馈 is_resolved=false 时，此问题才会被标记为待优化目标
    "is_optimization_target": bool,  # 是否为待优化目标（基于用户反馈自动设置）
    "optimization_target_since": Optional[datetime],  # 标记为待优化目标的时间
    
    # 验证记录
    "verification_records": [
        {
            "verification_id": str,
            "test_plan_id": str,
            "timestamp": datetime,
            "new_answer": str,
            "new_chunks": [...],
            "similarity_score": float,
            "effect_rating": str,
            "user_comment": Optional[str]
        }
    ],
    
    # 决策记录
    "decision_records": [
        {
            "decision_id": str,
            "test_plan_id": str,
            "timestamp": datetime,
            "decision": str,
            "reason": str,
            "operator": str
        }
    ],
    
    "created_at": datetime,
    "updated_at": datetime
}

Indexes:
- created_at (descending)
- status
- classification.severity
- classification.priority
- question (text search)
```

### Test Plan Collection

```python
Collection: test_plans

{
    "test_plan_id": str,         # UUID
    "name": str,                # 测试计划名称
    "description": Optional[str], # 描述
    "version": int,             # 版本号
    "parent_plan_id": Optional[str],  # 父测试计划 ID
    
    # 测试内容
    "question_ids": [str],      # 包含的问题 ID 列表
    "optimization_summary": {    # 优化摘要
        "operations": [         # 执行的优化操作
            {
                "type": str,   # "merge | split | adjust_boundary"
                "chunk_ids": [str],
                "timestamp": datetime
            }
        ],
        "affected_documents": [str],  # 受影响的文档 ID 列表
        "affected_chunks": [str]     # 受影响的 chunk ID 列表
    },
    
    # 测试结果
    "status": str,              # "draft | running | completed | failed"
    "started_at": Optional[datetime],
    "completed_at": Optional[datetime],
    "results": {
        "total": int,
        "better": int,
        "same": int,
        "worse": int,
        "failed": int
    },
    
    # 决策
    "decision": {
        "recommendation": str,   # "continue_optimization | stop_optimization | rollback"
        "reason": str,
        "impact_analysis": {
            "affected_questions": int,
            "improvement_rate": float,
            "regression_rate": float
        },
        "risk_assessment": {
            "level": str,       # "low | medium | high"
            "potential_issues": [str]
        },
        "cost_assessment": {
            "remaining_issues": int,
            "estimated_effort": str
        },
        "next_actions": [str]
    },
    
    "created_at": datetime,
    "updated_at": datetime,
    "created_by": str           # 创建者
}

Indexes:
- created_at (descending)
- status
- version
- created_by
```

### Verification Records Collection

```python
Collection: verification_records

{
    "verification_id": str,       # UUID
    "question_id": str,           # 关联的问题 ID
    "test_plan_id": str,         # 关联的测试计划 ID
    
    "original_answer": str,
    "new_answer": str,
    "original_chunks": [...],
    "new_chunks": [...],
    
    "similarity_score": float,
    "chunk_changes": {
        "added": int,
        "removed": int,
        "same": int
    },
    "score_changes": {
        "original_avg": float,
        "new_avg": float,
        "improvement": float
    },
    
    "effect_rating": str,
    "user_comment": Optional[str],
    
    "timestamp": datetime
}

Indexes:
- question_id
- test_plan_id
- timestamp (descending)
- effect_rating
```

## API Design

### Question Management APIs

#### GET /api/questions
获取问题列表

**Query Parameters:**
- `page`: int (default: 1)
- `page_size`: int (default: 20)
- `status`: Optional[str] (discovered | analyzing | optimizing | verifying | resolved | closed)
- `severity`: Optional[str] (low | medium | high | critical)
- `type`: Optional[str] (factual | explanatory | operational | comparative)
- `keyword`: Optional[str]
- `document_id`: Optional[str]
- `start_date`: Optional[datetime]
- `end_date`: Optional[datetime]

**Response:**
```json
{
  "total": 100,
  "page": 1,
  "page_size": 20,
  "questions": [
    {
      "question_id": "uuid",
      "question": "问题内容",
      "answer": "答案内容",
      "classification": {
        "type": "factual",
        "severity": "high",
        "scope": "single_document",
        "root_cause": "chunk_too_small",
        "priority": 7
      },
      "status": "discovered",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### POST /api/questions
创建问题记录

**Request Body:**
```json
{
  "question": "问题内容",
  "answer": "答案内容",
  "retrieved_chunks": [...],
  "retrieval_params": {...},
  "generation_params": {...},
  "classification": {
    "type": "factual",
    "severity": "high",
    "scope": "single_document",
    "root_cause": "chunk_too_small"
  },
  "related_questions": ["uuid1", "uuid2"],
  "related_chunks": ["chunk_id1", "chunk_id2"]
}
```

**Response:**
```json
{
  "question_id": "uuid",
  "status": "discovered",
  "priority": 7,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### GET /api/questions/{question_id}
获取问题详情

**Response:**
```json
{
  "question_id": "uuid",
  "question": "问题内容",
  "answer": "答案内容",
  "retrieved_chunks": [...],
  "retrieval_params": {...},
  "generation_params": {...},
  "classification": {...},
  "related_questions": [...],
  "related_chunks": [...],
  "status": "discovered",
  "status_history": [...],
  "user_feedback": {...},
  "verification_records": [...],
  "decision_records": [...],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /api/questions/{question_id}/classification
更新问题分类

**Request Body:**
```json
{
  "type": "factual",
  "severity": "high",
  "scope": "single_document",
  "root_cause": "chunk_too_small"
}
```

**Response:**
```json
{
  "question_id": "uuid",
  "classification": {
    "type": "factual",
    "severity": "high",
    "scope": "single_document",
    "root_cause": "chunk_too_small",
    "priority": 7
  },
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PUT /api/questions/{question_id}/status
更新问题状态

**Request Body:**
```json
{
  "status": "analyzing",
  "comment": "开始分析根因"
}
```

**Response:**
```json
{
  "question_id": "uuid",
  "status": "analyzing",
  "status_history": [
    {
      "status": "discovered",
      "timestamp": "2024-01-01T00:00:00Z",
      "operator": "user",
      "comment": null
    },
    {
      "status": "analyzing",
      "timestamp": "2024-01-01T01:00:00Z",
      "operator": "user",
      "comment": "开始分析根因"
    }
  ],
  "updated_at": "2024-01-01T01:00:00Z"
}
```

### Root Cause Analysis APIs

#### POST /api/questions/{question_id}/analyze-root-cause
分析问题根因

**Response:**
```json
{
  "question_id": "uuid",
  "root_cause_analysis": {
    "possible_causes": [
      {
        "cause": "chunk_too_small",
        "confidence": 0.85,
        "evidence": "检索到的 chunks 内容不完整"
      }
    ],
    "related_chunks": [
      {
        "chunk_id": "uuid",
        "content": "chunk 内容",
        "score": 0.75,
        "status": "active"
      }
    ],
    "optimization_suggestions": [
      {
        "type": "merge",
        "chunk_ids": ["chunk_id1", "chunk_id2"],
        "reason": "合并这两个 chunks 可以提供更完整的上下文"
      }
    ]
  },
  "analyzed_at": "2024-01-01T00:00:00Z"
}
```

### Test Plan Management APIs

#### POST /api/test-plans
创建测试计划

**Request Body:**
```json
{
  "name": "测试计划名称",
  "description": "描述",
  "question_ids": ["uuid1", "uuid2", "uuid3"],
  "optimization_summary": {
    "operations": [
      {
        "type": "merge",
        "chunk_ids": ["chunk_id1", "chunk_id2"],
        "timestamp": "2024-01-01T00:00:00Z"
      }
    ],
    "affected_documents": ["doc_id1"],
    "affected_chunks": ["chunk_id1", "chunk_id2"]
  }
}
```

**Response:**
```json
{
  "test_plan_id": "uuid",
  "name": "测试计划名称",
  "version": 1,
  "status": "draft",
  "question_ids": ["uuid1", "uuid2", "uuid3"],
  "created_at": "2024-01-01T00:00:00Z",
  "created_by": "user"
}
```

#### POST /api/test-plans/{test_plan_id}/execute
执行测试计划

**Response:**
```json
{
  "test_plan_id": "uuid",
  "status": "running",
  "started_at": "2024-01-01T00:00:00Z"
}
```

#### GET /api/test-plans/{test_plan_id}/status
获取测试计划状态

**Response:**
```json
{
  "test_plan_id": "uuid",
  "status": "running",
  "progress": {
    "total": 10,
    "completed": 5,
    "failed": 0,
    "percentage": 0.5
  },
  "started_at": "2024-01-01T00:00:00Z"
}
```

#### GET /api/test-plans/{test_plan_id}/results
获取测试计划结果

**Response:**
```json
{
  "test_plan_id": "uuid",
  "status": "completed",
  "results": {
    "total": 10,
    "better": 7,
    "same": 2,
    "worse": 1,
    "failed": 0
  },
  "decision": {
    "recommendation": "continue_optimization",
    "reason": "改进率 70%，回退率 10%，建议继续优化",
    "impact_analysis": {
      "affected_questions": 10,
      "improvement_rate": 0.7,
      "regression_rate": 0.1
    },
    "risk_assessment": {
      "level": "medium",
      "potential_issues": ["可能影响其他问题"]
    },
    "cost_assessment": {
      "remaining_issues": 3,
      "estimated_effort": "medium"
    },
    "next_actions": [
      "继续优化 chunk_id3 和 chunk_id4",
      "处理剩余的 3 个问题",
      "监控是否有新问题产生"
    ]
  },
  "completed_at": "2024-01-01T01:00:00Z"
}
```

### Verification APIs

#### POST /api/questions/{question_id}/retest
重新测试问题

**Response:**
```json
{
  "verification_id": "uuid",
  "question_id": "uuid",
  "test_plan_id": "uuid",
  "original_answer": "原始答案",
  "new_answer": "新答案",
  "original_chunks": [...],
  "new_chunks": [...],
  "similarity_score": 0.85,
  "chunk_changes": {
    "added": 2,
    "removed": 1,
    "same": 3
  },
  "score_changes": {
    "original_avg": 0.75,
    "new_avg": 0.82,
    "improvement": 0.07
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### GET /api/questions/{question_id}/verifications
获取验证记录列表

**Response:**
```json
{
  "question_id": "uuid",
  "verifications": [
    {
      "verification_id": "uuid",
      "test_plan_id": "uuid",
      "timestamp": "2024-01-01T00:00:00Z",
      "similarity_score": 0.85,
      "effect_rating": "better"
    }
  ]
}
```

#### POST /api/questions/{question_id}/verifications/{verification_id}/rate
评估优化效果

**Request Body:**
```json
{
  "effect_rating": "better",
  "comment": "答案质量明显提升"
}
```

**Response:**
```json
{
  "verification_id": "uuid",
  "effect_rating": "better",
  "comment": "答案质量明显提升",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Decision Support APIs

#### GET /api/test-plans/{test_plan_id}/decision
获取决策建议

**Response:**
```json
{
  "test_plan_id": "uuid",
  "decision": {
    "recommendation": "continue_optimization",
    "reason": "改进率 70%，回退率 10%，建议继续优化",
    "impact_analysis": {
      "affected_questions": 10,
      "improvement_rate": 0.7,
      "regression_rate": 0.1
    },
    "risk_assessment": {
      "level": "medium",
      "potential_issues": ["可能影响其他问题"]
    },
    "cost_assessment": {
      "remaining_issues": 3,
      "estimated_effort": "medium"
    },
    "next_actions": [
      "继续优化 chunk_id3 和 chunk_id4",
      "处理剩余的 3 个问题",
      "监控是否有新问题产生"
    ]
  }
}
```

#### POST /api/test-plans/{test_plan_id}/decision
记录决策

**Request Body:**
```json
{
  "decision": "continue_optimization",
  "reason": "改进率 70%，回退率 10%，决定继续优化"
}
```

**Response:**
```json
{
  "test_plan_id": "uuid",
  "decision": {
    "recommendation": "continue_optimization",
    "reason": "改进率 70%，回退率 10%，决定继续优化",
    "operator": "user",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

### Batch Test APIs

#### POST /api/questions/batch-retest
批量重新测试

**Request Body:**
```json
{
  "question_ids": ["uuid1", "uuid2", "uuid3"]
}
```

**Response:**
```json
{
  "batch_id": "uuid",
  "total": 3,
  "completed": 3,
  "failed": 0,
  "results": [
    {
      "question_id": "uuid1",
      "verification_id": "uuid",
      "status": "success",
      "similarity_score": 0.85
    }
  ]
}
```

#### GET /api/batch/{batch_id}/status
获取批量测试状态

**Response:**
```json
{
  "batch_id": "uuid",
  "total": 10,
  "completed": 5,
  "failed": 0,
  "progress": 0.5
}
```

## Frontend UI Design

### Page 1: 问题列表页面

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│  问题管理                                    [创建问题]  │
├─────────────────────────────────────────────────────────┤
│  筛选:                                                 │
│  [状态: 全部 ▼] [严重程度: 全部 ▼] [类型: 全部 ▼]      │
│  [搜索框: 输入关键词...]                                │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐ │
│  │ [☑] 问题: 如何使用系统进行文档上传？             │ │
│  │      类型: 事实性 | 严重: 高 | 优先级: 7      │ │
│  │      状态: discovered | 时间: 2024-01-01 10:00 │ │
│  │      [查看详情] [分析根因] [标记]                │ │
│  ├──────────────────────────────────────────────────┤ │
│  │ [☑] 问题: 系统支持哪些文档格式？                 │ │
│  │      类型: 解释性 | 严重: 中 | 优先级: 5      │ │
│  │      状态: analyzing | 时间: 2024-01-01 11:00  │ │
│  │      [查看详情] [分析根因] [标记]                │ │
│  └──────────────────────────────────────────────────┘ │
│                                                         │
│  [批量验证] [批量标记] [导出]                           │
│                                                         │
│  < 1 2 3 4 5 >                                         │
└─────────────────────────────────────────────────────────┘
```

### Page 2: 问题详情页面

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│  问题详情                                  [返回列表]   │
├─────────────────────────────────────────────────────────┤
│  问题: 如何使用系统进行文档上传？                        │
│  分类: 事实性 | 严重: 高 | 优先级: 7                  │
│  状态: discovered → analyzing → optimizing → verifying   │
├─────────────────────────────────────────────────────────┤
│  原始答案 (2024-01-01 10:00)                            │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 要使用系统进行文档上传，请按照以下步骤操作：...   │ │
│  └──────────────────────────────────────────────────┘ │
│                                                         │
│  检索的 Chunks:                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │ [✓] Chunk 1 (评分: 0.80) [相关]            │ │
│  │ [✓] Chunk 2 (评分: 0.75) [相关]            │ │
│  │ [✗] Chunk 3 (评分: 0.70) [不相关]           │ │
│  └──────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  根因分析:                                              │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 可能的原因:                                     │ │
│  │  • chunk 太小 (置信度: 85%)                   │ │
│  │  • chunk 边界不合理 (置信度: 70%)             │ │
│  │                                                │ │
│  │ 相关的 Chunks:                                  │ │
│  │  • Chunk 1 (相关)                              │ │
│  │  • Chunk 2 (相关)                              │ │
│  │                                                │ │
│  │ 优化建议:                                       │ │
│  │  • 合并 Chunk 1 和 Chunk 2                      │ │
│  │  • 调整 Chunk 3 的边界                        │ │
│  └──────────────────────────────────────────────────┘ │
│                                                         │
│  [创建测试计划] [标记状态] [关联问题]                   │
└─────────────────────────────────────────────────────────┘
```

### Page 3: 测试计划页面

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│  测试计划: Chunk 优化验证 v1              [返回列表]   │
├─────────────────────────────────────────────────────────┤
│  状态: completed | 版本: 1 | 创建者: user            │
│  开始时间: 2024-01-01 10:00 | 完成时间: 2024-01-01 11:00 │
├─────────────────────────────────────────────────────────┤
│  优化摘要:                                              │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 执行的操作:                                     │ │
│  │  • 合并 Chunk 1 和 Chunk 2                    │ │
│  │  • 拆分 Chunk 3                             │ │
│  │                                                │ │
│  │ 受影响的文档: doc_id1                            │ │
│  │ 受影响的 Chunks: chunk_id1, chunk_id2, chunk_id3 │ │
│  └──────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  测试结果:                                              │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 总数: 10 | 更好: 7 | 相同: 2 | 更差: 1     │ │
│  │ 改进率: 70% | 回退率: 10%                     │ │
│  │                                                │ │
│  │ [查看详细结果] [导出报告]                       │ │
│  └──────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  决策建议:                                              │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 建议: 继续优化 ✓                                │ │
│  │ 理由: 改进率 70%，回退率 10%，建议继续优化     │ │
│  │                                                │ │
│  │ 影响范围分析:                                   │ │
│  │  • 受影响的问题: 10                              │ │
│  │  • 改进率: 70%                                 │ │
│  │  • 回退率: 10%                                 │ │
│  │                                                │ │
│  │ 风险评估:                                       │ │
│  │  • 风险等级: 中                                 │ │
│  │  • 可能产生的新问题: 可能影响其他问题               │ │
│  │                                                │ │
│  │ 成本评估:                                       │ │
│  │  • 剩余问题: 3                                  │ │
│  │  • 预估工作量: 中                               │ │
│  │                                                │ │
│  │ 下一步行动:                                     │ │
│  │  1. 继续优化 chunk_id3 和 chunk_id4             │ │
│  │  2. 处理剩余的 3 个问题                         │ │
│  │  3. 监控是否有新问题产生                       │ │
│  └──────────────────────────────────────────────────┘ │
│                                                         │
│  [继续优化] [停止优化] [回滚优化] [记录决策]           │
└─────────────────────────────────────────────────────────┘
```

### Page 4: 验证结果对比页面

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│  验证结果对比                              [返回详情]   │
├─────────────────────────────────────────────────────────┤
│  问题: 如何使用系统进行文档上传？                        │
│  验证时间: 2024-01-02 14:30                          │
├─────────────────────────────────────────────────────────┤
│  原始答案 (2024-01-01 10:00)                            │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 要使用系统进行文档上传，请按照以下步骤操作：...   │ │
│  └──────────────────────────────────────────────────┘ │
│                                                         │
│  新答案 (2024-01-02 14:30)                             │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 要使用系统进行文档上传，请按照以下步骤操作：...   │ │
│  │ [差异高亮显示]                                    │ │
│  └──────────────────────────────────────────────────┘ │
│                                                         │
│  相似度: 85% | 优化效果: [✓更好] [○相同] [○更差]       │
├─────────────────────────────────────────────────────────┤
│  原始检索 Chunks (平均评分: 0.75)                      │
│  ┌──────────────────────────────────────────────────┐ │
│  │ [×] Chunk 1 (评分: 0.80)                         │ │
│  │ [✓] Chunk 2 (评分: 0.75) [相同]                 │ │
│  │ [×] Chunk 3 (评分: 0.70)                         │ │
│  └──────────────────────────────────────────────────┘ │
│                                                         │
│  新检索 Chunks (平均评分: 0.82)                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │ [+] Chunk 4 (评分: 0.85) [新增]                 │ │
│  │ [✓] Chunk 2 (评分: 0.75) [相同]                 │ │
│  │ [+] Chunk 5 (评分: 0.80) [新增]                 │ │
│  └──────────────────────────────────────────────────┘ │
│                                                         │
│  Chunk 变化: 新增 2, 删除 1, 相同 1                     │
│  评分改进: +0.07                                        │
├─────────────────────────────────────────────────────────┤
│  评论: [________________________] [提交]                │
└─────────────────────────────────────────────────────────┘
```

### Page 5: 验证历史和趋势分析页面

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│  验证历史                                  [返回详情]   │
├─────────────────────────────────────────────────────────┤
│  问题: 如何使用系统进行文档上传？                        │
├─────────────────────────────────────────────────────────┤
│  验证记录:                                              │
│  ┌──────────────────────────────────────────────────┐ │
│  │ [☑] 验证 1 (2024-01-02 14:30)              │ │
│  │      相似度: 85% | 效果: 更好                  │ │
│  │      [查看详情]                                   │ │
│  ├──────────────────────────────────────────────────┤ │
│  │ [☑] 验证 2 (2024-01-03 10:00)              │ │
│  │      相似度: 90% | 效果: 更好                  │ │
│  │      [查看详情]                                   │ │
│  ├──────────────────────────────────────────────────┤ │
│  │ [☑] 验证 3 (2024-01-04 15:30)              │ │
│  │      相似度: 92% | 效果: 更好                  │ │
│  │      [查看详情]                                   │ │
│  └──────────────────────────────────────────────────┘ │
│                                                         │
│  [对比选中的验证] [导出报告]                           │
├─────────────────────────────────────────────────────────┤
│  答案相似度趋势:                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │  ↑                                            │ │
│  │  │    ●──●──●                                 │ │
│  │  │   85% 90% 92%                              │ │
│  │  └──────────────────────→                       │ │
│  │    验证1 验证2 验证3                          │ │
│  └──────────────────────────────────────────────────┘ │
│                                                         │
│  检索相关性评分趋势:                                    │
│  ┌──────────────────────────────────────────────────┐ │
│  │  ↑                                            │ │
│  │  │    ●──●──●                                 │ │
│  │  │   0.75 0.82 0.88                          │ │
│  │  └──────────────────────→                       │ │
│  │    验证1 验证2 验证3                          │ │
│  └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Key Technical Solutions

### 1. 问题优先级计算

**方案**: 基于严重程度和影响范围自动计算优先级

```python
class PriorityCalculator:
    SEVERITY_WEIGHTS = {
        "low": 1,
        "medium": 3,
        "high": 5,
        "critical": 10
    }
    
    SCOPE_WEIGHTS = {
        "single_document": 1,
        "multi_document": 3,
        "global": 5
    }
    
    def calculate_priority(self, severity: str, scope: str) -> int:
        severity_weight = self.SEVERITY_WEIGHTS[severity]
        scope_weight = self.SCOPE_WEIGHTS[scope]
        
        # 优先级 = 严重程度权重 × 0.6 + 影响范围权重 × 0.4
        priority = int(severity_weight * 0.6 + scope_weight * 0.4)
        
        # 归一化到 1-10
        return min(max(priority, 1), 10)
```

### 2. 决策建议算法

**方案**: 基于测试结果综合判断

```python
class DecisionSupportService:
    def generate_decision(self, test_plan: TestPlan) -> dict:
        results = test_plan.results
        improvement_rate = results['better'] / results['total']
        regression_rate = results['worse'] / results['total']
        
        # 决策建议
        if improvement_rate > 0.7 and regression_rate < 0.3:
            recommendation = "continue_optimization"
            reason = f"改进率 {improvement_rate:.0%}，回退率 {regression_rate:.0%}，建议继续优化"
        elif improvement_rate < 0.3 and regression_rate < 0.3:
            recommendation = "stop_optimization"
            reason = f"改进率 {improvement_rate:.0%}，回退率 {regression_rate:.0%}，建议停止优化"
        elif regression_rate > 0.3:
            recommendation = "rollback"
            reason = f"回退率 {regression_rate:.0%}，建议回滚优化"
        else:
            recommendation = "continue_optimization"
            reason = "建议继续优化"
        
        # 影响范围分析
        impact_analysis = {
            "affected_questions": results['total'],
            "improvement_rate": improvement_rate,
            "regression_rate": regression_rate
        }
        
        # 风险评估
        risk_level = self._assess_risk(regression_rate, improvement_rate)
        potential_issues = self._identify_potential_issues(test_plan)
        
        # 成本评估
        remaining_issues = results['same'] + results['worse']
        estimated_effort = self._estimate_effort(remaining_issues)
        
        # 下一步行动
        next_actions = self._generate_next_actions(
            recommendation, 
            remaining_issues, 
            test_plan.optimization_summary
        )
        
        return {
            "recommendation": recommendation,
            "reason": reason,
            "impact_analysis": impact_analysis,
            "risk_assessment": {
                "level": risk_level,
                "potential_issues": potential_issues
            },
            "cost_assessment": {
                "remaining_issues": remaining_issues,
                "estimated_effort": estimated_effort
            },
            "next_actions": next_actions
        }
    
    def _assess_risk(self, regression_rate: float, improvement_rate: float) -> str:
        if regression_rate > 0.3:
            return "high"
        elif regression_rate > 0.1 or improvement_rate < 0.5:
            return "medium"
        else:
            return "low"
    
    def _identify_potential_issues(self, test_plan: TestPlan) -> List[str]:
        issues = []
        if test_plan.results['worse'] > 0:
            issues.append("可能影响其他问题")
        if test_plan.results['same'] > test_plan.results['total'] * 0.5:
            issues.append("优化效果不明显")
        return issues
    
    def _estimate_effort(self, remaining_issues: int) -> str:
        if remaining_issues < 3:
            return "low"
        elif remaining_issues < 7:
            return "medium"
        else:
            return "high"
    
    def _generate_next_actions(
        self, 
        recommendation: str, 
        remaining_issues: int,
        optimization_summary: dict
    ) -> List[str]:
        actions = []
        
        if recommendation == "continue_optimization":
            actions.append("继续优化相关 chunks")
            if remaining_issues > 0:
                actions.append(f"处理剩余的 {remaining_issues} 个问题")
            actions.append("监控是否有新问题产生")
        elif recommendation == "stop_optimization":
            actions.append("关闭已解决的问题")
            if remaining_issues > 0:
                actions.append(f"标记剩余的 {remaining_issues} 个问题为低优先级")
        elif recommendation == "rollback":
            actions.append("回滚 chunk 优化操作")
            actions.append("重新分析问题根因")
        
        return actions
```

### 3. 根因分析

**方案**: 基于检索结果分析问题可能的原因

```python
class RootCauseAnalysisService:
    def analyze_root_cause(self, question: Question) -> dict:
        retrieved_chunks = question.retrieved_chunks
        scores = [c['score'] for c in retrieved_chunks]
        avg_score = sum(scores) / len(scores)
        
        possible_causes = []
        
        # 分析相关性评分
        if avg_score < 0.6:
            possible_causes.append({
                "cause": "chunk_too_small",
                "confidence": 0.85,
                "evidence": f"检索到的 chunks 平均相关性评分较低 ({avg_score:.2f})"
            })
        
        # 分析 chunks 内容
        contents = [c['content'] for c in retrieved_chunks]
        total_length = sum(len(c) for c in contents)
        avg_length = total_length / len(contents)
        
        if avg_length < 200:
            possible_causes.append({
                "cause": "chunk_too_small",
                "confidence": 0.75,
                "evidence": f"检索到的 chunks 平均长度较短 ({avg_length:.0f} 字符)"
            })
        elif avg_length > 1000:
            possible_causes.append({
                "cause": "chunk_too_large",
                "confidence": 0.70,
                "evidence": f"检索到的 chunks 平均长度较长 ({avg_length:.0f} 字符)"
            })
        
        # 分析 chunks 边界
        for i, chunk in enumerate(retrieved_chunks):
            if i > 0:
                prev_chunk = retrieved_chunks[i - 1]
                if self._is_boundary_issue(prev_chunk, chunk):
                    possible_causes.append({
                        "cause": "boundary_issue",
                        "confidence": 0.65,
                        "evidence": f"Chunk {i} 和 Chunk {i+1} 之间可能存在边界问题"
                    })
        
        # 标记相关 chunks
        related_chunks = [
            {
                "chunk_id": c['chunk_id'],
                "content": c['content'][:100],
                "score": c['score'],
                "status": "active"
            }
            for c in retrieved_chunks
        ]
        
        # 生成优化建议
        optimization_suggestions = []
        for cause in possible_causes:
            if cause['cause'] == 'chunk_too_small':
                optimization_suggestions.append({
                    "type": "merge",
                    "chunk_ids": [c['chunk_id'] for c in retrieved_chunks[:2]],
                    "reason": "合并这两个 chunks 可以提供更完整的上下文"
                })
            elif cause['cause'] == 'chunk_too_large':
                optimization_suggestions.append({
                    "type": "split",
                    "chunk_ids": [retrieved_chunks[0]['chunk_id']],
                    "reason": "拆分这个 chunk 可以提高检索精度"
                })
        
        return {
            "possible_causes": possible_causes,
            "related_chunks": related_chunks,
            "optimization_suggestions": optimization_suggestions
        }
    
    def _is_boundary_issue(self, chunk1: dict, chunk2: dict) -> bool:
        content1 = chunk1['content']
        content2 = chunk2['content']
        
        # 检查句子是否在中间被切断
        if content1.endswith('。') or content1.endswith('！') or content1.endswith('？'):
            return False
        
        # 检查是否有不完整的句子
        if not content1.endswith(('。', '！', '？', '，', '；')):
            return True
        
        return False
```

### 4. 趋势分析

**方案**: 基于多次验证结果分析优化趋势

```python
class TrendAnalysisService:
    def analyze_trend(self, verifications: List[VerificationRecord]) -> dict:
        if len(verifications) < 2:
            return {"trend": "insufficient_data"}
        
        similarity_scores = [v.similarity_score for v in verifications]
        avg_scores = [v.score_changes['new_avg'] for v in verifications]
        
        # 分析相似度趋势
        similarity_trend = self._analyze_trend(similarity_scores)
        
        # 分析评分趋势
        score_trend = self._analyze_trend(avg_scores)
        
        # 分析 chunks 变化趋势
        chunk_changes = [v.chunk_changes for v in verifications]
        chunk_trend = self._analyze_chunk_trend(chunk_changes)
        
        return {
            "similarity_trend": similarity_trend,
            "score_trend": score_trend,
            "chunk_trend": chunk_trend,
            "overall_trend": self._determine_overall_trend(
                similarity_trend, 
                score_trend, 
                chunk_trend
            )
        }
    
    def _analyze_trend(self, values: List[float]) -> str:
        if len(values) < 2:
            return "insufficient_data"
        
        # 计算线性回归斜率
        x = list(range(len(values)))
        y = values
        n = len(values)
        
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi ** 2 for xi in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        if slope > 0.01:
            return "improving"
        elif slope < -0.01:
            return "declining"
        else:
            return "stable"
    
    def _analyze_chunk_trend(self, chunk_changes: List[dict]) -> str:
        if len(chunk_changes) < 2:
            return "insufficient_data"
        
        # 分析 chunks 变化是否趋于稳定
        added_changes = [c['added'] for c in chunk_changes]
        removed_changes = [c['removed'] for c in chunk_changes]
        
        added_variance = np.var(added_changes)
        removed_variance = np.var(removed_changes)
        
        if added_variance < 1 and removed_variance < 1:
            return "stabilizing"
        elif added_variance > 4 or removed_variance > 4:
            return "fluctuating"
        else:
            return "moderate"
    
    def _determine_overall_trend(
        self, 
        similarity_trend: str, 
        score_trend: str, 
        chunk_trend: str
    ) -> str:
        if similarity_trend == "improving" and score_trend == "improving":
            return "strong_improvement"
        elif similarity_trend == "declining" or score_trend == "declining":
            return "declining"
        elif chunk_trend == "stabilizing":
            return "stabilizing"
        else:
            return "moderate"
```

### 5. 答案相似度计算

**方案**: 使用 sentence-transformers 计算语义相似度，结合 difflib 计算文本相似度

```python
from sentence_transformers import SentenceTransformer
import difflib
import numpy as np

class SimilarityService:
    def __init__(self):
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        # 语义相似度
        embeddings1 = self.model.encode(text1)
        embeddings2 = self.model.encode(text2)
        semantic_sim = self._cosine_similarity(embeddings1, embeddings2)
        
        # 文本相似度
        text_sim = difflib.SequenceMatcher(None, text1, text2).ratio()
        
        # 综合相似度 (语义 70%, 文本 30%)
        return semantic_sim * 0.7 + text_sim * 0.3
    
    def _cosine_similarity(self, vec1, vec2) -> float:
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
```

### 6. Chunk 变化检测

**方案**: 基于 chunk_id 检测新增、删除、相同的 chunks

```python
class ComparisonService:
    def detect_chunk_changes(self, original_chunks, new_chunks):
        original_ids = {c['chunk_id'] for c in original_chunks}
        new_ids = {c['chunk_id'] for c in new_chunks}
        
        added = new_ids - original_ids
        removed = original_ids - new_ids
        same = original_ids & new_ids
        
        return {
            'added': len(added),
            'removed': len(removed),
            'same': len(same),
            'added_chunks': [c for c in new_chunks if c['chunk_id'] in added],
            'removed_chunks': [c for c in original_chunks if c['chunk_id'] in removed],
            'same_chunks': [c for c in new_chunks if c['chunk_id'] in same]
        }
```

### 7. 文本差异高亮

**方案**: 使用 difflib 生成差异并高亮显示

```python
class DiffHighlightService:
    def highlight_diff(self, original: str, new: str) -> str:
        differ = difflib.Differ()
        diff = list(differ.compare(original.splitlines(), new.splitlines()))
        
        highlighted = []
        for line in diff:
            if line.startswith('+ '):
                highlighted.append(f'<span class="added">{line[2:]}</span>')
            elif line.startswith('- '):
                highlighted.append(f'<span class="removed">{line[2:]}</span>')
            else:
                highlighted.append(line[2:])
        
        return '\n'.join(highlighted)
```

### 8. 批量测试并发控制

**方案**: 使用 asyncio 控制并发数量

```python
import asyncio

class BatchTestService:
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def batch_retest(self, question_ids: List[str]):
        tasks = []
        for question_id in question_ids:
            task = self._retest_with_semaphore(question_id)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    
    async def _retest_with_semaphore(self, question_id: str):
        async with self.semaphore:
            return await self._retest_question(question_id)
```

## Integration with Existing System

### 1. 与 RAG 系统集成

**集成点**: 复用现有的检索和生成逻辑

```python
class VerificationUseCase:
    def __init__(self, rag_use_case, question_repository):
        self.rag_use_case = rag_use_case
        self.question_repository = question_repository
    
    async def retest_question(self, question_id: str):
        # 获取原始问题
        question = await self.question_repository.get_by_id(question_id)
        
        # 使用 RAG 系统重新检索和生成
        result = await self.rag_use_case.ask(
            question=question['question'],
            retrieval_params=question['retrieval_params']
        )
        
        # 创建验证记录
        verification = await self._create_verification_record(
            question, result
        )
        
        return verification
```

### 2. 与 Chunk 管理集成

**集成点**: 在 chunk 合并后提供验证入口

```javascript
// chunks.js
async function mergeChunks(chunkId1, chunkId2, mergeType) {
    const response = await fetch('/api/chunks/merge', {
        method: 'POST',
        body: JSON.stringify({
            chunk_id_1: chunkId1,
            chunk_id_2: chunkId2,
            merge_type: mergeType
        })
    });
    
    const result = await response.json();
    
    if (result.success) {
        // 显示"创建测试计划"按钮
        showCreateTestPlanButton();
    }
}

function showCreateTestPlanButton() {
    const button = document.createElement('button');
    button.textContent = '创建测试计划';
    button.onclick = () => {
        window.location.href = '/test-plans/create';
    };
    document.body.appendChild(button);
}
```

## Performance Optimization

### 1. 问题历史查询优化

**方案**: 使用 Qdrant 的过滤和分页功能

```python
async def get_questions(
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    severity: Optional[str] = None
):
    filters = []
    if status:
        filters.append(
            models.FieldCondition(
                key="status",
                match=models.MatchValue(value=status)
            )
        )
    if severity:
        filters.append(
            models.FieldCondition(
                key="classification.severity",
                match=models.MatchValue(value=severity)
            )
        )
    
    # 使用 Qdrant 的 scroll API 分页
    offset = (page - 1) * page_size
    points, _ = client.scroll(
        collection_name="question_history",
        scroll_filter=models.Filter(must=filters),
        limit=page_size,
        offset=offset
    )
    
    return points
```

### 2. 批量测试性能优化

**方案**: 使用连接池和缓存

```python
class BatchTestService:
    def __init__(self):
        self.qdrant_client = QdrantClient(
            url="http://localhost:6333",
            prefer_grpc=True
        )
        self.llm_cache = LRUCache(maxsize=100)
    
    async def batch_retest(self, question_ids: List[str]):
        # 并发执行，使用连接池
        tasks = [
            self._retest_question(qid)
            for qid in question_ids
        ]
        return await asyncio.gather(*tasks)
```

## Security Considerations

### 1. 输入验证

```python
from pydantic import BaseModel, validator

class QuestionCreateRequest(BaseModel):
    question: str
    answer: str
    classification: QuestionClassification
    
    @validator('question')
    def validate_question(cls, v):
        if len(v) < 10 or len(v) > 1000:
            raise ValueError('问题长度必须在 10-1000 字符之间')
        return v

class QuestionClassification(BaseModel):
    type: str
    severity: str
    scope: str
    root_cause: str
    
    @validator('type')
    def validate_type(cls, v):
        allowed = ['factual', 'explanatory', 'operational', 'comparative']
        if v not in allowed:
            raise ValueError(f'Invalid type: {v}')
        return v
    
    @validator('severity')
    def validate_severity(cls, v):
        allowed = ['low', 'medium', 'high', 'critical']
        if v not in allowed:
            raise ValueError(f'Invalid severity: {v}')
        return v
```

### 2. 权限控制

```python
from fastapi import Depends, HTTPException

async def verify_user(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user

@app.post("/api/questions")
async def create_question(
    request: QuestionCreateRequest,
    user: User = Depends(verify_user)
):
    # 创建问题
    question = await question_repository.create(request.dict(), user.id)
    return question
```

## Error Handling

### 1. 统一错误响应

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

app.add_exception_handler(HTTPException, http_exception_handler)
```

### 2. 批量测试错误处理

```python
async def batch_retest(self, question_ids: List[str]):
    results = []
    for question_id in question_ids:
        try:
            result = await self._retest_question(question_id)
            results.append({
                'question_id': question_id,
                'status': 'success',
                'result': result
            })
        except Exception as e:
            results.append({
                'question_id': question_id,
                'status': 'failed',
                'error': str(e)
            })
    
    return results
```
