# 本地 Embedding 模型降级方案

## 概述

本方案提供了一个本地 embedding 模型的降级实现，用于替代 SiliconFlow API 服务，避免 API 限制和网络依赖。

## 配置说明

### 环境变量配置

在 `.env` 文件中添加以下配置：

```bash
# 使用本地 embedding 服务（默认为 True）
USE_LOCAL_EMBEDDING=True

# 本地 embedding 模型名称
LOCAL_EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5
```

### 可用的本地模型

推荐使用的本地 embedding 模型：

1. **BAAI/bge-small-zh-v1.5** (推荐)
   - 维度：512
   - 模型大小：约 100MB
   - 性能：优秀的中文语义理解
   - 适合：资源受限环境

2. **BAAI/bge-base-zh-v1.5**
   - 维度：768
   - 模型大小：约 400MB
   - 性能：更好的语义理解
   - 适合：性能要求较高的场景

3. **BAAI/bge-large-zh-v1.5**
   - 维度：1024
   - 模型大小：约 1.3GB
   - 性能：最佳语义理解
   - 适合：高性能服务器环境

## 实现细节

### 本地 Embedding 服务

文件位置：`src/aitechpioneer/infrastructure/local_embedding.py`

主要特性：
- 使用 `sentence-transformers` 库加载本地模型
- 支持批量 embedding 生成
- 自动模型缓存和加载
- 标准化输出向量

### 服务选择逻辑

文件位置：`src/aitechpioneer/application/use_cases.py`

```python
def create_embedding_service() -> EmbeddingServicePort:
    if settings.use_local_embedding:
        logger.info(f"Using local embedding service with model: {settings.local_embedding_model}")
        return LocalEmbeddingService(model_name=settings.local_embedding_model)
    else:
        logger.info(f"Using SiliconFlow embedding service with model: {settings.embedding_model}")
        return SiliconFlowEmbeddingService()
```

## 使用方法

### 1. 切换到本地模型

在 `.env` 文件中设置：
```bash
USE_LOCAL_EMBEDDING=True
LOCAL_EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5
```

### 2. 切换到 SiliconFlow API

在 `.env` 文件中设置：
```bash
USE_LOCAL_EMBEDDING=False
SILICONFLOW_API_KEY=your_api_key_here
```

### 3. 重启服务

修改配置后需要重启 API 服务：
```bash
# 停止当前服务
# 重新启动
python3.11 -m uvicorn aitechpioneer.interfaces.api:app --host 0.0.0.0 --port 8001 --reload
```

## 性能对比

| 方案 | 首次加载 | 单次请求 | 批量请求 | 限制 |
|------|---------|---------|---------|------|
| 本地模型 | 5-10秒 | 50-100ms | 200-500ms | 无限制 |
| SiliconFlow API | 即时 | 200-500ms | 1-2秒 | RPM限制 |

## 优缺点

### 本地模型

**优点：**
- 无 API 限制
- 无网络依赖
- 数据隐私安全
- 成本低（一次性下载）

**缺点：**
- 首次加载需要时间
- 占用本地存储空间
- 需要 GPU 加速才能达到最佳性能

### SiliconFlow API

**优点：**
- 无需本地存储
- 即时可用
- 服务器端优化

**缺点：**
- 有 API 限制
- 依赖网络连接
- 数据需要上传到第三方
- 可能产生费用

## 故障排除

### 1. 模型下载失败

如果模型下载失败，可以手动下载：

```bash
# 使用 huggingface-cli 下载
huggingface-cli download BAAI/bge-small-zh-v1.5
```

### 2. 内存不足

如果遇到内存不足，可以：
- 使用更小的模型（如 `BAAI/bge-small-zh-v1.5`）
- 减少 batch size
- 增加系统内存

### 3. 性能问题

如果性能不佳，可以：
- 使用 GPU 加速（需要 CUDA）
- 使用更大的模型（如 `BAAI/bge-large-zh-v1.5`）
- 优化 chunk 大小和数量

## 监控和日志

系统会记录以下信息：
- 模型加载状态
- embedding 生成时间
- 批量处理进度
- 错误和异常信息

查看日志：
```bash
# 查看服务器日志
# 日志会显示使用的 embedding 服务类型
```

## 最佳实践

1. **开发环境**：使用本地模型，避免 API 限制
2. **生产环境**：根据需求选择，考虑成本和性能
3. **混合使用**：可以根据场景动态切换
4. **监控性能**：定期检查 embedding 生成时间和质量
5. **备选方案**：保持两种方案都可用，以便快速切换

## 更新日志

- 2026-01-08: 初始实现，支持本地 embedding 模型降级方案
