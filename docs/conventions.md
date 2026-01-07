# Coding Conventions

## General

* 单一职责优先
* 明确命名胜过注释
* 禁止“临时写法”

## File Placement

* 业务逻辑 → domain/
* 流程控制 → application/
* IO / DB / LLM → infrastructure/
* 对外入口 → interfaces/

## Imports

* 禁止跨层反向 import
* domain 层不允许出现第三方 SDK

## When Unsure

* 优先放在 application/
* 并在代码中注明 TODO
