# Document Processing Module Specification

## Responsibility

* 文档清洗
* 文档处理流程

## Scope

* application/use_cases.py
* domain/services.py

## Allowed Files

* domain/services.py
* application/use_cases.py

## Forbidden

* 新增 domain 子模块
* 在 interfaces 实现逻辑

## Dependencies

* domain.models

## Notes

这是一个跨层模块，由 application 负责编排。
