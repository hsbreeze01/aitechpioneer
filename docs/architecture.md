# Project Architecture

本项目采用分层架构（Layered Architecture）：
domain / application / infrastructure / interfaces
禁止跨层反向依赖。

## Layers

### domain/

* 业务模型
* 业务规则
* 与具体技术无关
* 不允许依赖其他层

### application/

* 用例（Use Cases）
* 编排 domain 对象
* 不包含基础设施实现

### infrastructure/

* 数据库
* 外部 API
* 第三方服务
* 实现 domain 定义的接口

### interfaces/

* HTTP API
* CLI
* 消息消费入口
* 只做参数解析与调用 application

## Dependency Rules

* domain → ❌ application / infrastructure / interfaces
* application → ❌ infrastructure（只能依赖接口）
* interfaces → ✅ application
* infrastructure → ✅ domain / application
