# Interfaces Layer Specification

## Responsibility

* API
* CLI
* 前端界面（HTML/CSS/JavaScript）
* 用户交互逻辑

## Scope

src/project_name/interfaces
frontend/

## Allowed Files

* api.py
* cli.py
* frontend/**/*.html
* frontend/**/*.css
* frontend/**/*.js

## UI/UX Requirements

### 设计系统遵循
* 必须遵循 `docs/design-system.md` 中定义的设计规范
* 使用 CSS 变量定义颜色、字体、间距、阴影等
* 确保所有前端组件的一致性
* 不得使用硬编码的颜色值（除 #FFFFFF 和 #000000）

### 可访问性要求
* 所有前端界面必须符合 WCAG AA 标准
* 文本对比度至少 4.5:1
* 所有交互元素必须支持键盘导航
* 必须提供 ARIA 标签
* Focus 状态必须可见
* 屏幕阅读器兼容性
* 支持 prefers-reduced-motion

### 响应式设计
* 必须在以下断点测试和优化：375px, 768px, 1024px, 1440px
* 触摸目标最小 44x44px
* 使用 CSS Grid 和 Flexbox 实现灵活布局
* 提供移动优先的响应式设计

### 性能要求
* 动画时长 150-300ms
* 使用 transform 和 opacity 优化动画性能（避免触发重排）
* 图标使用 SVG（避免使用 emoji）
* 支持 prefers-reduced-motion
* 优化 CSS/JS 文件
* 避免布局抖动

### 组件规范
* 按钮必须有 hover/focus/disabled 状态
* 表单必须有验证反馈和错误提示
* 加载状态必须明确指示
* 空状态必须适当处理
* 所有交互元素必须有 cursor-pointer
* 所有图片必须有 alt 属性
* 表单 input 必须有 id 属性（用于 label 关联）

### UI/UX Skill 使用
* 参考 `.claude/skills/ui-ux-pro-max/SKILL.md` 了解 UI/UX 能力
* 使用 UI/UX Pro Max 能力进行设计决策
* 遵循 Anti-Patterns 避免常见错误
* 应用 Pre-Delivery Checklist

### UI/UX 工作流
* 遵循 `docs/ui-ux-workflow.md` 中定义的 UI/UX 开发工作流
  1. 需求分析
  2. 设计系统应用
  3. 响应式设计
  4. 可访问性检查
  5. 性能优化
  6. 代码实现
  7. 验证和测试

## Forbidden

* 业务逻辑（交由 application 层）
* 数据持久化（交由 infrastructure 层）
* 违反设计系统的样式
* 硬编码的颜色值（除 #FFFFFF 和 #000000）
* 使用 emoji 作为图标

## Dependencies

* application

## Notes

只做参数解析、结果返回和前端界面渲染。

前端开发完成后，必须运行 `scripts/validate_ui_ux.py` 进行验证。
