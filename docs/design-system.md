# RAG 系统设计系统

## 项目概述

**项目名称**: AI Tech Pioneer - RAG 系统
**产品类型**: AI/Chatbot Platform (Tech & SaaS)
**目标用户**: 开发者、企业用户、内容管理者
**核心功能**: 文档管理、智能检索、智能问答、Chunk管理

---

## 推荐设计系统

### PATTERN: Dashboard-Centric + Clean Interface

**布局策略**:
- Dashboard为主，功能模块化
- 清晰的信息层级
- 高效的数据展示

**转换目标**: 效率驱动，信息清晰
**CTA位置**: 顶部导航 + 关键操作按钮
**主要页面**:
  1. 首页 (Hero + Features)
  2. 文档管理 (列表 + 详情)
  3. 智能问答 (输入 + 结果)
  4. Chunk管理 (列表 + 操作)

---

## STYLE: Modern Tech UI

**关键词**: Clean, Professional, Data-Driven, Accessible
**最佳适用**: SaaS平台、开发者工具、AI系统
**性能**: Excellent | **可访问性**: WCAG AA

---

## COLORS

### 主色调
- **Primary**: `#6366f1` (Indigo)
  - 用途: 主要按钮、链接、强调元素
  - 情感: 专业、可信、现代
  
- **Secondary**: `#64748b` (Slate)
  - 用途: 次要按钮、边框、分隔线
  - 情感: 中性、稳定

### 功能色
- **Success**: `#10b981` (Emerald)
  - 用途: 成功状态、完成操作
  
- **Danger**: `#ef4444` (Red)
  - 用途: 错误、删除操作、警告
  
- **Warning**: `#f59e0b` (Amber)
  - 用途: 警告、待处理状态
  
- **Info**: `#3b82f6` (Blue)
  - 用途: 信息提示、加载状态

### 背景色
- **Primary**: `#ffffff` (White)
  - 用途: 主背景、卡片背景
  
- **Secondary**: `#f8fafc` (Slate-50)
  - 用途: 次要背景、页面背景
  
- **Tertiary**: `#f1f5f9` (Slate-100)
  - 用途: 悬停背景、分隔区域

### 文本色
- **Primary**: `#0f172a` (Slate-900)
  - 用途: 主要文本、标题
  
- **Secondary**: `#475569` (Slate-600)
  - 用途: 次要文本、描述
  
- **Tertiary**: `#94a3b8` (Slate-400)
  - 用途: 辅助文本、占位符

**说明**: 高对比度配色方案，确保文本可读性和专业感

---

## TYPOGRAPHY

### 字体组合
**主字体**: Inter
- Google Fonts: https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap
- 风格: 现代、清晰、技术感
- 最佳适用: SaaS平台、开发者工具

**字重使用**:
- **300 (Light)**: 辅助文本、标签
- **400 (Regular)**: 正文、描述
- **500 (Medium)**: 按钮、链接
- **600 (SemiBold)**: 小标题、强调
- **700 (Bold)**: 页面标题、Logo

**字号规范**:
- **H1**: 2.5rem (40px) - 页面主标题
- **H2**: 2rem (32px) - 区块标题
- **H3**: 1.5rem (24px) - 卡片标题
- **Body**: 1rem (16px) - 正文
- **Small**: 0.875rem (14px) - 辅助文本
- **XSmall**: 0.75rem (12px) - 标签、元数据

**行高**:
- 标题: 1.2
- 正文: 1.6
- 小文本: 1.4

---

## KEY EFFECTS

### 阴影系统
- **Shadow Sm**: `0 1px 2px 0 rgba(0, 0, 0, 0.05)`
  - 用途: 卡片、小元素
  
- **Shadow Md**: `0 4px 6px -1px rgba(0, 0, 0, 0.1)`
  - 用途: 悬停卡片、弹窗
  
- **Shadow Lg**: `0 10px 15px -3px rgba(0, 0, 0, 0.1)`
  - 用途: 模态框、重要卡片

### 过渡动画
- **Fast**: `150ms` - 按钮悬停、链接
- **Normal**: `200-300ms` - 卡片悬停、面板切换
- **Slow**: `500ms` - 页面切换、模态框

### 悬停状态
- 按钮悬停: 背景色加深 + 轻微上移
- 卡片悬停: 阴影增强 + 轻微放大
- 链接悬停: 颜色变化 + 下划线

---

## SPACING

### 间距系统 (基于 4px 网格)
- **xs**: 0.25rem (4px)
- **sm**: 0.5rem (8px)
- **md**: 1rem (16px)
- **lg**: 1.5rem (24px)
- **xl**: 2rem (32px)
- **2xl**: 3rem (48px)

### 应用场景
- **组件内**: sm - md
- **组件间**: md - lg
- **区块间**: lg - xl
- **页面边距**: xl - 2xl

---

## BORDER RADIUS

- **Sm**: 0.375rem (6px) - 按钮、标签
- **Md**: 0.5rem (8px) - 输入框、卡片
- **Lg**: 0.75rem (12px) - 模态框、大卡片

---

## AVOID (Anti-patterns)

### 避免使用
- ❌ 霓虹色、高饱和度渐变
- ❌ 过度动画、闪烁效果
- ❌ 纯深色模式（除非明确需求）
- ❌ AI紫色/粉色渐变（不适用于专业SaaS）
- ❌ Emoji作为图标（使用SVG: Heroicons/Lucide）
- ❌ 小于4.5:1的文本对比度

### 推荐使用
- ✅ 清晰的信息层级
- ✅ 一致的间距和布局
- ✅ 适当的留白
- ✅ 平滑的过渡动画
- ✅ 明确的交互反馈

---

## PRE-DELIVERY CHECKLIST

### 可访问性
- [ ] 所有可点击元素有 `cursor-pointer`
- [ ] 悬停状态有平滑过渡 (150-300ms)
- [ ] 浅色模式文本对比度 ≥ 4.5:1
- [ ] 键盘导航有可见的焦点状态
- [ ] 尊重 `prefers-reduced-motion` 设置

### 响应式设计
- [ ] 375px (移动端)
- [ ] 768px (平板)
- [ ] 1024px (桌面)
- [ ] 1440px (大屏)

### 代码质量
- [ ] 使用SVG图标代替Emoji
- [ ] 语义化HTML标签
- [ ] 一致的类名命名
- [ ] CSS变量定义完整
- [ ] 无内联样式（特殊情况除外）

---

## COMPONENT STYLES

### 按钮
- **Primary**: Indigo背景，白色文字，中等圆角
- **Secondary**: Slate背景，白色文字，中等圆角
- **Info**: 蓝色背景，白色文字
- **Success**: 绿色背景，白色文字
- **Danger**: 红色背景，白色文字
- **Small**: 较小字号和内边距

### 卡片
- 白色背景，中等阴影，中等圆角
- 悬停时阴影增强
- 内边距: lg

### 输入框
- 白色背景，浅色边框
- 聚焦时Indigo边框
- 圆角: md
- 内边距: sm - md

### 导航
- 固定顶部，白色背景，中等阴影
- 活动链接Indigo色
- 悬停链接颜色变化

### 表单
- 标签: Secondary色，中等字重
- 输入框: 宽度100%，适当间距
- 错误提示: Danger色，小字号

---

## RESPONSIVE BREAKPOINTS

- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px - 1440px
- **Large Desktop**: > 1440px

---

## PERFORMANCE TARGETS

- **首屏加载**: < 2s
- **交互响应**: < 100ms
- **动画帧率**: 60fps
- **可访问性评分**: AA级别

---

## TECH STACK

- **HTML5**: 语义化标签
- **CSS3**: CSS变量、Flexbox、Grid
- **JavaScript (ES6+)**: 原生JavaScript，无框架依赖
- **图标**: Heroicons (SVG)

---

## DESIGN TOKENS (CSS Variables)

```css
:root {
  /* Colors */
  --primary: #6366f1;
  --primary-hover: #4f46e5;
  --secondary: #64748b;
  --secondary-hover: #475569;
  --success: #10b981;
  --danger: #ef4444;
  --warning: #f59e0b;
  --info: #3b82f6;
  
  /* Backgrounds */
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --bg-tertiary: #f1f5f9;
  
  /* Text */
  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-tertiary: #94a3b8;
  
  /* Borders */
  --border-color: #e2e8f0;
  --border-hover: #cbd5e1;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  
  /* Radius */
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  
  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  --spacing-2xl: 3rem;
  
  /* Transitions */
  --transition-fast: 150ms;
  --transition-normal: 200-300ms;
  --transition-slow: 500ms;
  
  /* Font */
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
```

---

## PAGE-SPECIFIC GUIDELINES

### 首页 (index.html)
- Hero区域: 大标题、副标题、CTA按钮
- Features: 3列网格布局，图标+标题+描述
- 简洁、引导性强

### 文档管理 (documents.html)
- 列表视图: 表格或卡片网格
- 操作按钮: 查看、删除、重新切分
- 筛选和搜索: 顶部工具栏

### 智能问答 (qa.html)
- 输入区域: 大输入框+参数配置
- 结果区域: 清晰的问答展示
- 反馈机制: 满意度评价

### Chunk管理 (chunks.html)
- 列表视图: 卡片网格，显示chunk内容
- 批量操作: 复选框+合并按钮
- 筛选: 状态、类型筛选

---

## IMPLEMENTATION NOTES

1. **渐进式重构**: 逐步应用新设计系统，避免大规模破坏性更改
2. **向后兼容**: 保留现有功能，只更新样式
3. **测试覆盖**: 每个页面重构后进行测试
4. **性能监控**: 确保重构不影响加载性能
5. **用户反馈**: 收集用户对新UI的反馈

---

## VERSION HISTORY

- **v1.0**: 初始设计系统，基于ui-ux-pro-max-skill v2.0
- **Date**: 2025-01-16
