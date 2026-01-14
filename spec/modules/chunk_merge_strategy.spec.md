# Chunk Merge Strategy Specification

## Background

当前chunk合并策略采用"新版本chunk重写"方式，存在以下问题：
- 原chunk被物理删除，数据丢失风险高
- 并发操作可能导致竞态条件
- 无法追溯完整的chunk历史变更
- 撤销操作依赖merged_from字段，存在单点故障风险

## Goal

实现更安全的chunk合并策略，确保：
1. 原始数据永不丢失（软删除）
2. 支持完整的版本历史追溯
3. 提供安全的并发操作机制
4. 支持多级撤销操作

## Scope

* src/aitechpioneer/domain/models.py
* src/aitechpioneer/application/use_cases.py
* src/aitechpioneer/interfaces/api.py

## Allowed Changes

### Domain Layer (models.py)
1. 扩展Chunk模型，添加版本历史字段
2. 新增ChunkVersion模型，记录chunk的完整历史
3. 新增ChunkMergeRecord模型，记录合并操作历史
4. 修改ChunkStatus枚举，添加MERGED状态

### Application Layer (use_cases.py)
1. 重构merge_chunks方法，实现软删除策略
2. 重构undo_merge方法，支持多级撤销
3. 新增get_chunk_history方法，查询chunk历史
4. 新增get_merge_history方法，查询合并历史

### Interface Layer (api.py)
1. 新增GET /api/chunks/{chunk_id}/history 端点
2. 新增GET /api/merge-history 端点
3. 新增GET /api/chunks/{chunk_id}/versions 端点

## Forbidden

* 修改infrastructure层（数据库实现）
* 新增domain子模块
* 修改现有的DELETE /api/chunks/{chunk_id}端点行为

## Design Principles

### 1. 软删除策略
- 原chunk状态从ACTIVE改为MERGED
- 保留原chunk的所有数据和嵌入向量
- 通过inactive_reason记录合并信息

### 2. 版本控制系统
- 每个chunk维护版本链：version -> previous_version_id
- ChunkVersion表记录每个版本的完整快照
- 支持回滚到任意历史版本

### 3. 合并历史追踪
- ChunkMergeRecord记录每次合并操作
- 包含：操作时间、操作人、源chunk、目标chunk、操作类型
- 支持审计和追溯

### 4. 并发安全
- 使用乐观锁（version字段）防止并发冲突
- 合并操作检查chunk的当前version
- 冲突时返回错误，不自动重试

## Data Model Changes

### Chunk Model Extensions
```python
@dataclass
class Chunk:
    # 现有字段保持不变
    
    # 新增字段
    previous_version_id: Optional[UUID] = None  # 指向前一个版本
    is_latest_version: bool = True  # 是否为最新版本
    merge_record_id: Optional[UUID] = None  # 关联的合并记录ID
```

### New Models

#### ChunkVersion
```python
@dataclass
class ChunkVersion:
    version_id: UUID = field(default_factory=uuid4)
    chunk_id: UUID  # 关联的chunk ID
    version: int
    content: str
    embedding: List[float]
    status: ChunkStatus
    quality: ChunkQuality
    metadata: Optional[ChunkMetadata]
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "system"  # 操作人标识
```

#### ChunkMergeRecord
```python
@dataclass
class ChunkMergeRecord:
    record_id: UUID = field(default_factory=uuid4)
    merge_type: str  # "merge", "split", "undo_merge"
    source_chunk_ids: List[UUID]  # 源chunk列表
    target_chunk_id: UUID  # 目标chunk（合并后或撤销后的chunk）
    previous_state: Dict[str, Any]  # 操作前的状态快照
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "system"
    is_reversible: bool = True  # 是否可撤销
```

### ChunkStatus Enum Extension
```python
class ChunkStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    INACTIVE = "inactive"
    MERGED = "merged"  # 新增：已被合并
    SPLIT = "split"  # 新增：已被拆分
```

## Use Case Specifications

### UC-1: Safe Chunk Merge

**Preconditions:**
- chunk1和chunk2存在且状态为ACTIVE
- chunk1和chunk2属于同一文档
- chunk1和chunk2版本相同

**Process:**
1. 创建ChunkMergeRecord，记录操作前状态
2. 创建新的merged_chunk
3. 将chunk1和chunk2状态改为MERGED
4. 设置chunk1和chunk2的merge_record_id
5. 创建chunk1和chunk2的ChunkVersion快照
6. 插入merged_chunk到数据库
7. 更新merged_chunk的previous_version_id

**Postconditions:**
- chunk1和chunk2状态为MERGED，数据完整保留
- merged_chunk状态为ACTIVE
- ChunkMergeRecord记录完整
- 所有ChunkVersion快照已创建

**Error Handling:**
- 如果chunk不存在，抛出ChunkNotFoundError
- 如果chunk状态不是ACTIVE，抛出InvalidChunkStatusError
- 如果chunk版本不匹配，抛出VersionConflictError
- 如果合并失败，回滚所有状态变更

### UC-2: Multi-level Undo Merge

**Preconditions:**
- merged_chunk存在且状态为ACTIVE
- merged_chunk有merge_record_id
- 对应的ChunkMergeRecord存在且is_reversible=True

**Process:**
1. 获取merged_chunk的merge_record_id
2. 查询ChunkMergeRecord获取源chunk列表
3. 恢复源chunk状态为ACTIVE
4. 清除源chunk的merge_record_id
5. 将merged_chunk状态改为INACTIVE
6. 创建新的ChunkMergeRecord记录撤销操作
7. 创建merged_chunk的ChunkVersion快照

**Postconditions:**
- 源chunk恢复为ACTIVE状态
- merged_chunk状态为INACTIVE
- 两条ChunkMergeRecord存在（原始合并+撤销操作）
- 所有ChunkVersion快照完整

**Error Handling:**
- 如果merged_chunk不存在，抛出ChunkNotFoundError
- 如果合并记录不存在，抛出MergeRecordNotFoundError
- 如果合并不可撤销，抛出IrreversibleOperationError

### UC-3: Query Chunk History

**Preconditions:**
- chunk_id存在

**Process:**
1. 查询chunk的当前状态
2. 查询所有关联的ChunkVersion记录
3. 查询所有关联的ChunkMergeRecord
4. 按时间顺序构建历史链

**Postconditions:**
- 返回完整的历史记录列表
- 包含每次状态变更的时间、操作人、原因

### UC-4: Query Merge History

**Preconditions:**
- 无

**Process:**
1. 查询所有ChunkMergeRecord
2. 按时间倒序排列
3. 支持按document_id、chunk_id、时间范围过滤

**Postconditions:**
- 返回合并历史列表
- 包含完整的合并操作信息

## API Endpoints

### GET /api/chunks/{chunk_id}/history
查询chunk的完整历史

**Response:**
```json
{
  "chunk_id": "uuid",
  "current_version": 3,
  "versions": [
    {
      "version": 1,
      "status": "active",
      "content": "...",
      "created_at": "2024-01-01T00:00:00Z",
      "created_by": "system"
    },
    {
      "version": 2,
      "status": "merged",
      "content": "...",
      "created_at": "2024-01-02T00:00:00Z",
      "created_by": "user123",
      "merge_record_id": "uuid"
    }
  ],
  "merge_records": [
    {
      "record_id": "uuid",
      "merge_type": "merge",
      "source_chunk_ids": ["uuid1", "uuid2"],
      "target_chunk_id": "uuid3",
      "created_at": "2024-01-02T00:00:00Z",
      "created_by": "user123"
    }
  ]
}
```

### GET /api/merge-history
查询合并历史

**Query Parameters:**
- document_id (optional): 过滤文档
- chunk_id (optional): 过滤chunk
- start_date (optional): 开始日期
- end_date (optional): 结束日期
- limit (optional): 返回数量限制

**Response:**
```json
{
  "total": 100,
  "records": [
    {
      "record_id": "uuid",
      "merge_type": "merge",
      "source_chunk_ids": ["uuid1", "uuid2"],
      "target_chunk_id": "uuid3",
      "created_at": "2024-01-02T00:00:00Z",
      "created_by": "user123",
      "is_reversible": true
    }
  ]
}
```

### GET /api/chunks/{chunk_id}/versions
查询chunk的所有版本

**Response:**
```json
{
  "chunk_id": "uuid",
  "total_versions": 3,
  "versions": [
    {
      "version_id": "uuid",
      "version": 1,
      "content": "...",
      "embedding": [0.1, 0.2, ...],
      "status": "active",
      "quality": "high",
      "created_at": "2024-01-01T00:00:00Z",
      "created_by": "system"
    }
  ]
}
```

## Migration Strategy

### Phase 1: Data Model Extension
1. 扩展Chunk模型，添加新字段
2. 创建ChunkVersion和ChunkMergeRecord模型
3. 扩展ChunkStatus枚举

### Phase 2: Use Case Refactoring
1. 重构merge_chunks方法
2. 重构undo_merge方法
3. 实现新的查询方法

### Phase 3: API Extension
1. 添加新的API端点
2. 更新API文档

### Phase 4: Data Migration
1. 为现有chunk创建初始ChunkVersion记录
2. 迁移现有的merged_from数据到ChunkMergeRecord

## Testing Requirements

### Unit Tests
- 测试软删除逻辑
- 测试版本控制机制
- 测试合并记录创建
- 测试并发冲突处理

### Integration Tests
- 测试完整的合并流程
- 测试多级撤销流程
- 测试历史查询功能
- 测试并发合并操作

### Performance Tests
- 测试大量chunk的合并性能
- 测试历史查询性能
- 测试并发场景下的性能

## Rollback Plan

如果新策略出现问题，可以：
1. 回滚到原有的物理删除策略
2. 保留新的数据模型，但禁用新功能
3. 使用数据迁移脚本恢复原有行为

## Notes

- 所有操作必须记录操作人信息（created_by）
- ChunkVersion表应该定期归档历史数据
- 合并记录应该保留至少6个月
- 考虑添加合并操作的审批流程
