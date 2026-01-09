# Infrastructure Layer Specification

## Responsibility

* 数据库
* 缓存
* LLM / 外部服务

## Scope

src/project_name/infrastructure

## Allowed Files

* db.py
* cache.py
* llm.py

## Forbidden

* 包含业务规则

## Dependencies

* domain
* application
* 第三方库

## Notes

这是变化最频繁的层。
