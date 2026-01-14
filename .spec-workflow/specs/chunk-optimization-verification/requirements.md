# Requirements: Chunk Optimization Verification

## Overview

在用户发现 chunk 召回不符合预期并进行 chunk 优化（如合并）后，提供一个完整的验证和决策支持系统，帮助用户：
1. 系统化地管理问题和测试流程
2. 评估 chunk 优化的效果
3. 基于测试结果做出是否继续优化 chunk 的决策

## User Stories

### US-1: 问题分类和标记
**As a** 用户  
**I want to** 对发现的问题进行分类和严重程度标记  
**So that** 我可以系统化地管理问题，优先处理重要问题

**Acceptance Criteria**:
- 支持问题类型分类（事实性问题、解释性问题、操作性问题、对比性问题等）
- 支持严重程度标记（低、中、高、严重）
- 支持影响范围标记（单文档、多文档、全局）
- 支持问题根因标记（chunk太小、chunk太大、chunk边界不合理、chunk内容不完整等）
- 支持问题关联（标记多个问题可能由同一个chunk问题导致）
- 支持问题优先级自动计算（基于严重程度和影响范围）

### US-2: 问题生命周期管理
**As a** 用户  
**I want to** 系统化地管理问题从发现到解决的全流程  
**So that** 我可以清晰地追踪问题的处理进度

**Acceptance Criteria**:
- 问题状态流转：发现 → 分析 → 优化中 → 验证中 → 已解决 → 已关闭
- 自动记录每个状态的变更时间和操作人
- 支持问题状态回退（如：验证中 → 优化中）
- 支持问题合并（多个相似问题合并为一个）
- 支持问题拆分（一个复杂问题拆分为多个子问题）
- 显示问题处理时间线
- **仅记录用户反馈"没有解决问题"的问题-答案对作为待分析优化目标**
- **用户反馈"已解决"的问题不记录为待优化目标，直接标记为已解决状态**

### US-3: 测试计划管理
**As a** 用户  
**I want to** 创建和管理测试计划  
**So that** 我可以系统化地进行 chunk 优化验证

**Acceptance Criteria**:
- 支持创建测试计划（选择需要验证的问题）
- 支持测试计划版本管理（每次优化后创建新的测试计划）
- 支持测试计划对比（对比不同版本的测试结果）
- 支持测试计划导出（导出为 PDF 或 Excel）
- 支持测试计划分享（生成分享链接）
- 显示测试计划执行进度

### US-4: 多次验证结果对比
**As a** 用户  
**I want to** 对比多次验证的结果  
**So that** 我可以了解 chunk 优化的趋势和效果

**Acceptance Criteria**:
- 显示问题的所有验证记录
- 支持选择多个验证记录进行对比
- 显示答案相似度趋势图
- 显示检索相关性评分趋势图
- 显示 chunks 变化趋势图
- 支持导出验证结果对比报告

### US-5: 优化效果评估
**As a** 用户  
**I want to** 系统帮助我评估 chunk 优化的效果  
**So that** 我可以快速判断优化是否达到预期

**Acceptance Criteria**:
- 自动对比优化前后的答案质量
- 提供答案相似度评分
- 提供检索 chunks 的变化统计（新增、删除、变化的 chunks）
- 显示检索相关性评分的变化
- 支持用户手动标记优化效果（更好、相同、更差）
- 记录优化评估结果
- 提供优化效果总结报告

### US-6: 决策支持
**As a** 用户  
**I want to** 系统基于测试结果提供决策建议  
**So that** 我可以做出是否继续优化 chunk 的决策

**Acceptance Criteria**:
- 基于测试结果提供优化建议（继续优化、停止优化、回滚优化）
- 显示 chunk 优化影响范围分析（哪些问题受影响）
- 显示优化风险评估（可能产生的新问题）
- 显示优化成本评估（需要处理的问题数量）
- 提供下一步行动建议
- 支持用户记录决策理由
- 记录决策结果

### US-7: 问题根因分析
**As a** 用户  
**I want to** 系统帮助我分析问题的根本原因  
**So that** 我可以针对性地优化 chunk

**Acceptance Criteria**:
- 基于检索结果分析问题可能的原因
- 标记问题相关的 chunks
- 显示 chunks 的详细信息和状态
- 提供 chunk 优化建议（如：合并、拆分、调整边界）
- 显示 chunks 之间的关联关系
- 支持用户确认或修正根因分析结果

### US-8: 批量验证和汇总
**As a** 用户  
**I want to** 批量验证多个问题并查看汇总结果  
**So that** 我可以全面评估 chunk 优化的整体效果

**Acceptance Criteria**:
- 支持选择多个问题进行批量验证
- 显示批量验证的进度
- 提供批量验证结果的汇总统计
- 显示优化效果分布（更好、相同、更差的问题数量）
- 显示问题严重程度分布
- 支持按优化效果和严重程度筛选问题
- 支持导出批量验证结果

### US-9: Chunk 优化工作流集成
**As a** 用户  
**I want to** 在 chunk 优化后直接进入验证和决策流程  
**So that** 我可以快速完成优化验证和决策

**Acceptance Criteria**:
- 在 chunk 合并成功后，提供"创建测试计划"按钮
- 点击"创建测试计划"后，自动推荐相关问题
- 支持选择相关问题加入测试计划
- 执行测试计划后，自动显示决策建议
- 支持快速返回 chunk 管理页面继续优化

## Functional Requirements

### FR-1: 问题管理
- 问题分类（类型、严重程度、影响范围、根因）
- 问题关联（多个问题关联到同一个chunk）
- 问题生命周期管理（状态流转）
- 问题优先级计算
- 问题搜索和筛选
- **用户反馈处理：仅记录反馈"没有解决问题"的问题-答案对作为待分析优化目标**
- **用户反馈"已解决"的问题直接标记为已解决状态，不记录为待优化目标**

### FR-2: 测试计划管理
- 创建测试计划
- 测试计划版本管理
- 测试计划对比
- 测试计划导出
- 测试计划分享

### FR-3: 验证执行
- 重新测试问题
- 记录验证结果
- 计算答案相似度
- 计算 chunks 变化
- 计算评分变化

### FR-4: 结果对比
- 多次验证结果对比
- 趋势图展示
- 差异高亮
- 对比报告生成

### FR-5: 效果评估
- 自动评估答案质量变化
- 计算检索相关性评分变化
- 提供优化效果总结
- 支持用户手动评估

### FR-6: 决策支持
- 提供优化建议
- 影响范围分析
- 风险评估
- 成本评估
- 行动建议
- 决策记录

### FR-7: 根因分析
- 分析问题可能的原因
- 标记相关 chunks
- 提供 chunk 优化建议
- 显示 chunks 关联关系

### FR-8: 批量操作
- 批量验证
- 批量评估
- 批量导出
- 批量标记

### FR-9: Web API
- 问题管理 API
- 测试计划 API
- 验证执行 API
- 结果对比 API
- 决策支持 API
- 根因分析 API

### FR-10: Web UI
- 问题列表页面
- 问题详情页面
- 测试计划页面
- 验证结果对比页面
- 决策支持页面
- 根因分析页面

## Non-Functional Requirements

### NFR-1: Performance
- 问题查询响应时间 < 1s
- 验证执行响应时间 < 3s
- 批量验证支持 10+ 问题并发
- 结果对比计算 < 1s
- 决策支持分析 < 2s

### NFR-2: Scalability
- 支持存储 10,000+ 问题
- 支持存储 1,000+ 测试计划
- 支持快速检索和筛选
- 支持高并发验证

### NFR-3: Usability
- 直观的界面设计
- 清晰的问题分类
- 简单的操作流程
- 友好的决策建议
- 丰富的可视化图表

### NFR-4: Reliability
- 问题数据持久化
- 验证结果准确记录
- 决策建议可靠
- 数据一致性保证

## Data Requirements

### DR-1: Question Structure
```python
{
    "question_id": str,           # 唯一标识符
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
            "test_plan_id": str,      # 关联的测试计划 ID
            "timestamp": datetime,
            "new_answer": str,
            "new_chunks": [...],
            "similarity_score": float,
            "effect_rating": str,     # "better | same | worse"
            "user_comment": Optional[str]
        }
    ],
    
    # 决策记录
    "decision_records": [
        {
            "decision_id": str,
            "test_plan_id": str,
            "timestamp": datetime,
            "decision": str,         # "continue_optimization | stop_optimization | rollback"
            "reason": str,
            "operator": str
        }
    ],
    
    "created_at": datetime,
    "updated_at": datetime
}
```

### DR-2: Test Plan Structure
```python
{
    "test_plan_id": str,         # 唯一标识符
    "name": str,                # 测试计划名称
    "description": Optional[str], # 描述
    "version": int,             # 版本号
    "parent_plan_id": Optional[str],  # 父测试计划 ID（用于版本管理）
    
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
            "improvement_rate": float,  # 改进率（better / total）
            "regression_rate": float     # 回退率（worse / total）
        },
        "risk_assessment": {
            "level": str,       # "low | medium | high"
            "potential_issues": [str]
        },
        "cost_assessment": {
            "remaining_issues": int,
            "estimated_effort": str  # "low | medium | high"
        },
        "next_actions": [str]   # 建议的下一步行动
    },
    
    "created_at": datetime,
    "updated_at": datetime,
    "created_by": str           # 创建者
}
```

### DR-3: Verification Record Structure
```python
{
    "verification_id": str,
    "question_id": str,
    "test_plan_id": str,
    
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
    
    "effect_rating": str,       # "better | same | worse"
    "user_comment": Optional[str],
    
    "timestamp": datetime
}
```

## Constraints

### C-1: Technology Stack
- 后端：Python 3.12+
- 向量数据库：Qdrant 1.16.3
- LLM：DeepSeek API
- 前端：React
- Web 框架：FastAPI
- 文本相似度：sentence-transformers + difflib
- 图表库：Chart.js 或 ECharts

### C-2: Architecture
- 遵循分层架构
- Spec-driven 开发模式
- 严格的架构边界

### C-3: Integration
- 与现有的 RAG 系统集成
- 与 chunk 管理功能集成
- 复用现有的检索和生成逻辑

## Assumptions

### A-1: User Behavior
- 用户会在发现问题后进行 chunk 优化
- 用户希望系统化地管理问题和测试流程
- 用户希望基于测试结果做出决策

### A-2: Data Consistency
- 问题历史记录完整
- chunk 状态变更会立即生效
- 检索和生成逻辑稳定

## Dependencies

### D-1: Existing Systems
- RAG 问答系统
- Chunk 管理系统
- Qdrant 向量数据库
- DeepSeek API

### D-2: Python Libraries
- sentence-transformers
- difflib
- fastapi
- uvicorn
- pydantic
- matplotlib（可选，用于生成图表）

## Open Questions

### OQ-1: 问题优先级计算算法
**问题**: 如何计算问题优先级？

**解决方案**: 优先级 = 严重程度权重 × 0.6 + 影响范围权重 × 0.4
- 严重程度：low=1, medium=3, high=5, critical=10
- 影响范围：single_document=1, multi_document=3, global=5

### OQ-2: 决策建议算法
**问题**: 如何提供决策建议？

**解决方案**: 基于以下因素综合判断：
- 改进率（better / total）：> 70% 建议继续，< 30% 建议停止
- 回退率（worse / total）：> 30% 建议回滚
- 严重问题数量：高严重程度问题 > 3 建议继续优化

### OQ-3: 测试计划版本管理
**问题**: 如何管理测试计划版本？

**解决方案**: 每次优化后创建新版本，保留历史版本用于对比

## Out of Scope

- 自动优化 chunk（仅提供验证和决策支持）
- A/B 测试框架
- 多用户问题历史隔离
- 问题历史导出为文档
- 复杂的统计分析功能
