# UI/UX 开发工作流

本文档定义了在全栈架构师智能体中整合 UI/UX Pro Max 能力的开发工作流程。

## 前置条件

在开始任何 UI/UX 开发任务之前，必须：

1. ✅ 阅读 [design-system.md](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/docs/design-system.md) 了解设计规范
2. ✅ 阅读 [.claude/skills/ui-ux-pro-max/SKILL.md](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/.claude/skills/ui-ux-pro-max/SKILL.md) 了解 UI/UX 能力
3. ✅ 阅读 [spec/layers/interfaces.spec.md](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/spec/layers/interfaces.spec.md) 了解接口层要求
4. ✅ 确认 [AGENT.md](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/AGENT.md) 中的 UI/UX 规则

## 开发流程

### 阶段 1: 需求分析

**目标**: 理解用户需求和业务目标

**任务**:
- 理解用户想要实现的功能
- 确定页面类型（Dashboard、Hero、Content-First、E-commerce、SaaS）
- 识别关键用户流程
- 分析目标用户群体和使用场景

**输出**:
- 页面类型和设计模式
- 关键用户流程图
- 功能优先级列表

**参考**: UI/UX Pro Max Skill 中的 "Design Pattern Recognition" 部分

---

### 阶段 2: 设计系统应用

**目标**: 应用设计系统规范

**任务**:
- 从 [design-system.md](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/docs/design-system.md) 选择合适的颜色、字体、间距
- 使用 CSS 变量确保一致性
- 遵循组件规范（按钮、卡片、表单等）
- 确定风格类型（Modern Tech UI、Soft UI Evolution、Bold & Vibrant、Minimalist）

**输出**:
- CSS 变量定义
- 组件样式规范
- 设计系统应用方案

**参考**: [design-system.md](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/docs/design-system.md) 中的 "组件设计规范"

---

### 阶段 3: 响应式设计

**目标**: 确保在所有设备上正常显示

**任务**:
- 在 375px（移动端）测试和优化
- 在 768px（平板）调整布局
- 在 1024px（笔记本）优化网格
- 在 1440px（桌面）最大化利用空间
- 确保触摸目标最小 44x44px

**输出**:
- 媒体查询定义
- 响应式布局方案
- 移动端优化策略

**参考**: [design-system.md](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/docs/design-system.md) 中的 "响应式断点"

---

### 阶段 4: 可访问性检查

**目标**: 确保 WCAG AA 合规

**任务**:
- 检查文本对比度（至少 4.5:1）
- 确保键盘导航可用
- 添加 ARIA 标签
- 确保 Focus 状态可见
- 测试屏幕阅读器兼容性
- 支持 prefers-reduced-motion

**输出**:
- 可访问性测试报告
- ARIA 标签清单
- 键盘导航方案

**参考**: UI/UX Pro Max Skill 中的 "Accessibility First" 部分

---

### 阶段 5: 性能优化

**目标**: 优化加载和交互性能

**任务**:
- 压缩 CSS/JS 文件
- 优化 SVG 图标
- 使用 transform 和 opacity 优化动画
- 实现资源懒加载
- 避免布局抖动
- 确保动画时长 150-300ms

**输出**:
- 性能优化方案
- 资源优化清单
- 动画性能测试

**参考**: UI/UX Pro Max Skill 中的 "Performance" 部分

---

### 阶段 6: 代码实现

**目标**: 在 interfaces 层实现前端代码

**任务**:
- 在 `frontend/` 目录下创建 HTML 文件
- 在 `frontend/static/css/` 目录下创建 CSS 文件
- 在 `frontend/static/js/` 目录下创建 JavaScript 文件
- 使用 CSS 变量和组件模板
- 遵循分层架构规则（interfaces 层只做参数解析和结果返回）

**输出**:
- HTML 文件
- CSS 文件
- JavaScript 文件

**参考**: [spec/layers/interfaces.spec.md](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/spec/layers/interfaces.spec.md)

---

### 阶段 7: 验证和测试

**目标**: 确保所有规范都得到满足

**任务**:
- 运行 `scripts/validate_ui_ux.py` 进行 UI/UX 验证
- 运行 `scripts/validate_spec.py` 进行 Spec 验证
- 手动测试响应式布局
- 测试键盘导航
- 测试屏幕阅读器兼容性
- 测试动画性能

**输出**:
- 验证报告
- 测试结果
- 问题清单

**参考**: [AGENT.md](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/AGENT.md) 中的 "Validation Obligation"

---

## 验证清单

### 视觉设计

- [ ] 颜色使用一致（使用 CSS 变量）
- [ ] 间距和对齐正确
- [ ] 视觉层次清晰
- [ ] 字体使用恰当
- [ ] 动画平滑（150-300ms）
- [ ] 无硬编码颜色值（除纯黑纯白）

### 可访问性

- [ ] 文本对比度 ≥ 4.5:1
- [ ] ARIA 标签完整
- [ ] 键盘导航可用
- [ ] Focus 状态可见
- [ ] 屏幕阅读器兼容
- [ ] 支持 prefers-reduced-motion
- [ ] 所有 img 标签有 alt 属性
- [ ] 表单 input 有 id 属性

### 响应式

- [ ] 375px（移动端）正常显示
- [ ] 768px（平板）布局优化
- [ ] 1024px（笔记本）网格调整
- [ ] 1440px（桌面）空间利用
- [ ] 触摸目标 ≥ 44x44px
- [ ] 使用 CSS Grid 和 Flexbox

### 性能

- [ ] CSS/JS 已优化
- [ ] 无布局抖动
- [ ] 动画流畅
- [ ] 资源懒加载
- [ ] 使用 SVG 图标（无 emoji）
- [ ] 使用 transform 和 opacity

### 组件规范

- [ ] 按钮有 hover/focus/disabled 状态
- [ ] 表单有验证反馈和错误提示
- [ ] 加载状态明确
- [ ] 空状态处理
- [ ] 所有交互元素有 cursor-pointer

---

## 常见问题

### Q1: 如何选择设计模式？

**A**: 根据页面类型和业务目标选择：
- **Dashboard-Centric**: 数据驱动、效率优先（如管理后台、分析平台）
- **Hero-Centric**: 情感驱动、转化优先（如落地页、营销页面）
- **Content-First**: 阅读友好、排版优先（如博客、文档）
- **E-commerce**: 产品中心、转化优化（如电商网站）
- **SaaS**: 专业、功能丰富（如 SaaS 应用）

### Q2: 如何确保可访问性？

**A**: 遵循以下原则：
1. 使用语义化 HTML 标签
2. 为所有交互元素添加 ARIA 标签
3. 确保足够的颜色对比度
4. 支持键盘导航
5. 提供 Focus 状态
6. 测试屏幕阅读器兼容性

### Q3: 如何优化动画性能？

**A**: 遵循以下原则：
1. 使用 transform 和 opacity（避免触发重排）
2. 动画时长 150-300ms
3. 使用 will-change 优化
4. 支持 prefers-reduced-motion
5. 避免复杂的动画

### Q4: 如何处理跨浏览器兼容性？

**A**: 遵循以下原则：
1. 使用现代 CSS 特性（Grid、Flexbox、Custom Properties）
2. 提供降级方案
3. 测试主流浏览器（Chrome、Firefox、Safari、Edge）
4. 使用 Autoprefixer 自动添加前缀

### Q5: 如何避免常见的 UI/UX 错误？

**A**: 参考 UI/UX Pro Max Skill 中的 "Anti-Patterns to Avoid"：
- 避免鲜艳的霓虹色
- 避免生硬的动画和过渡
- 避免深色模式对比度不足
- 避免通用的 AI 紫色/粉色渐变
- 避免使用 emoji 作为图标
- 避免隐藏导航
- 避免不清晰的 CTA
- 避免缺少加载状态
- 避免糟糕的错误处理
- 避免不一致的交互

---

## 工具和资源

### 设计工具
- [Figma](https://www.figma.com/) - UI/UX 设计工具
- [Sketch](https://www.sketch.com/) - 矢量设计工具
- [Adobe XD](https://www.adobe.com/products/xd.html) - 原型设计工具

### 可访问性工具
- [WAVE](https://wave.webaim.org/) - 可访问性评估工具
- [axe DevTools](https://www.deque.com/axe/devtools/) - 可访问性测试工具
- [Lighthouse](https://developers.google.com/web/tools/lighthouse) - 性能和可访问性审计

### 性能工具
- [PageSpeed Insights](https://pagespeed.web.dev/) - 性能分析工具
- [WebPageTest](https://www.webpagetest.org/) - 网站性能测试
- [Chrome DevTools](https://developers.google.com/web/tools/chrome-devtools) - 浏览器开发工具

### 颜色工具
- [Coolors](https://coolors.co/) - 配色方案生成器
- [Adobe Color](https://color.adobe.com/) - 颜色主题创建工具
- [Contrast Checker](https://webaim.org/resources/contrastchecker/) - 对比度检查工具

---

## 参考文档

- [design-system.md](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/docs/design-system.md) - 设计系统规范
- [architecture.md](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/docs/architecture.md) - 项目架构
- [conventions.md](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/docs/conventions.md) - 代码规范
- [.claude/skills/ui-ux-pro-max/SKILL.md](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/.claude/skills/ui-ux-pro-max/SKILL.md) - UI/UX Pro Max Skill
- [spec/layers/interfaces.spec.md](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/spec/layers/interfaces.spec.md) - 接口层规范
- [AGENT.md](file:///Users/lancer.zhang/ProjectNIO/aitechpioneer/AGENT.md) - 智能体行为规则

---

## 版本历史

- **v1.0** (2026-01-17): 初始版本，定义 UI/UX 开发工作流
