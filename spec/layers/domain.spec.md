# Domain Layer Specification

## Responsibility

* 业务模型
* 业务规则
* 与技术实现无关

## Scope

src/project_name/domain

## Allowed Files

* models.py
* services.py
* ports.py

## Forbidden

* 访问 infrastructure
* 调用第三方 SDK
* IO / 网络 / 数据库

## Dependencies

* 仅允许 Python 标准库

## Notes

这是系统中最稳定的层。
