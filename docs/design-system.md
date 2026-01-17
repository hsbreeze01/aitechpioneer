# RAG 文档问答系统 - 设计系统

## 设计系统生成

**TARGET: RAG 文档问答系统**

+----------------------------------------------------------------------------------------+
|  PATTERN: Dashboard-Centric + Modern Tech UI                                           |
|     Focus: Data-driven, efficiency-focused interface                                       |
|     Goals:                                                                              |
|       - 快速文档检索和问答                                                               |
|       - 清晰的数据展示和统计                                                              |
|       - 高效的文档和 Chunk 管理                                                           |
|       - 专业的技术文档界面                                                               |
|     Sections:                                                                          |
|       1. 首页 (Hero + Features + Stats)                                                |
|       2. 文档管理 (列表 + 上传 + 详情)                                                     |
|       3. 智能检索 (搜索 + 结果展示)                                                        |
|       4. 智能问答 (输入 + 答案 + 反馈 + 历史)                                              |
|       5. Chunk 管理 (列表 + 合并 + 编辑)                                                   |
|                                                                                        |
|  STYLE: Modern Tech UI                                                                  |
|     Keywords: Clean, professional, data-driven, minimal, efficient                      |
|     Best For: SaaS, analytics, developer tools, technical platforms                   |
|     Performance: Excellent | Accessibility: WCAG AA                                    |
|                                                                                        |
|  COLORS:                                                                               |
|     Primary:    #6366F1 (Indigo 500) - 主要操作和强调色                                     |
|     Primary Hover: #4F46E5 (Indigo 600)                                                  |
|     Secondary:  #64748B (Slate 500) - 次要操作和辅助信息                                    |
|     Secondary Hover: #475569 (Slate 600)                                                |
|     Success:    #10B981 (Emerald 500) - 成功状态和积极反馈                                    |
|     Danger:     #EF4444 (Red 500) - 错误和危险操作                                       |
|     Warning:    #F59E0B (Amber 500) - 警告和注意                                         |
|     Info:       #3B82F6 (Blue 500) - 信息提示                                             |
|     Background: #F8FAFC (Slate 50) - 页面背景                                              |
|     Surface:    #FFFFFF (White) - 卡片和面板背景                                             |
|     Text Primary:   #0F172A (Slate 900) - 主要文本                                         |
|     Text Secondary: #475569 (Slate 600) - 次要文本                                       |
|     Text Tertiary:  #94A3B8 (Slate 400) - 辅助文本                                       |
|     Border:      #E2E8F0 (Slate 200) - 边框和分隔线                                      |
|     Notes: Professional tech palette with good contrast and readability                  |
|                                                                                        |
|  TYPOGRAPHY: Inter / JetBrains Mono                                                       |
|     Mood: Clean, modern, technical, readable                                         |
|     Best For: SaaS, developer tools, documentation platforms                          |
|     Google Fonts: https://fonts.google.com/share?selection?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500 |
|     Scale:                                                                              |
|       - H1: 2.5rem (40px) - 页面标题                                                    |
|       - H2: 2rem (32px) - 章节标题                                                     |
|       - H3: 1.5rem (24px) - 小节标题                                                     |
|       - H4: 1.25rem (20px) - 卡片标题                                                    |
|       - Body: 1rem (16px) - 正文                                                         |
|       - Small: 0.875rem (14px) - 标签和元数据                                             |
|       - XSmall: 0.75rem (12px) - 辅助文本                                               |
|     Line Height: 1.6 for body, 1.4 for headings                                         |
|                                                                                        |
|  SPACING SYSTEM:                                                                        |
|     Scale: 4px base (0.25rem)                                                          |
|     - xs: 0.25rem (4px)                                                                |
|     - sm: 0.5rem (8px)                                                                |
|     - md: 1rem (16px)                                                                 |
|     - lg: 1.5rem (24px)                                                               |
|     - xl: 2rem (32px)                                                                 |
|     - 2xl: 3rem (48px)                                                                |
|     - 3xl: 4rem (64px)                                                                |
|                                                                                        |
|  BORDER RADIUS:                                                                         |
|     - sm: 0.375rem (6px)                                                              |
|     - md: 0.5rem (8px)                                                                |
|     - lg: 0.75rem (12px)                                                              |
|                                                                                        |
|  SHADOWS:                                                                              |
|     - sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05)                                            |
|     - md: 0 4px 6px -1px rgba(0, 0, 0, 0.1)                                          |
|     - lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1)                                         |
|                                                                                        |
|  KEY EFFECTS:                                                                          |
|     Smooth transitions (150-300ms) + Subtle hover states + Clean focus indicators    |
|     Transform: translateY(-1px) on hover for buttons                                        |
|     Focus: 2px solid outline + 4px offset + color-matched box-shadow                    |
|                                                                                        |
|  AVOID (Anti-patterns):                                                                |
|     Bright neon colors + Harsh animations + Dark mode without proper contrast    |
|     AI purple/pink gradients + Emojis as icons (use SVG: Heroicons/Lucide)    |
|     Generic stock photos + Overuse of shadows/gradients                                    |
|                                                                                        |
|  PRE-DELIVERY CHECKLIST:                                                               |
|     [ ] No emojis as icons (use SVG: Heroicons/Lucide)                                 |
|     [ ] cursor-pointer on all clickable elements                                       |
|     [ ] Hover states with smooth transitions (150-300ms)                               |
|     [ ] Light mode: text contrast 4.5:1 minimum                                        |
|     [ ] Focus states visible for keyboard nav                                          |
|     [ ] prefers-reduced-motion respected                                               |
|     [ ] Responsive: 375px, 768px, 1024px, 1440px                                       |
|     [ ] Touch targets minimum 44x44px                                                    |
|     [ ] Consistent spacing and sizing                                                    |
|     [ ] Clear visual hierarchy                                                           |
|     [ ] Accessible color combinations                                                    |
+----------------------------------------------------------------------------------------+

## 组件设计规范

### Buttons (按钮)

#### Primary Button
```css
.btn-primary {
    background: #6366F1;
    color: white;
    padding: 0.625rem 1.25rem;
    border-radius: 0.5rem;
    font-weight: 600;
    transition: all 150ms;
}

.btn-primary:hover {
    background: #4F46E5;
    transform: translateY(-1px);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.btn-primary:focus {
    outline: 2px solid #6366F1;
    outline-offset: 2px;
    box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2);
}
```

#### Secondary Button
```css
.btn-secondary {
    background: #64748B;
    color: white;
    padding: 0.625rem 1.25rem;
    border-radius: 0.5rem;
    font-weight: 600;
    transition: all 150ms;
}

.btn-secondary:hover {
    background: #475569;
    transform: translateY(-1px);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.btn-secondary:focus {
    outline: 2px solid #64748B;
    outline-offset: 2px;
    box-shadow: 0 0 0 4px rgba(100, 116, 139, 0.2);
}
```

#### Success/Danger/Warning/Info Buttons
```css
.btn-success {
    background: #10B981;
    color: white;
}

.btn-success:hover {
    background: #059669;
}

.btn-success:focus {
    outline: 2px solid #10B981;
    outline-offset: 2px;
    box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.2);
}

.btn-danger {
    background: #EF4444;
    color: white;
}

.btn-danger:hover {
    background: #DC2626;
}

.btn-danger:focus {
    outline: 2px solid #EF4444;
    outline-offset: 2px;
    box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.2);
}

.btn-warning {
    background: #F59E0B;
    color: white;
}

.btn-warning:hover {
    background: #D97706;
}

.btn-warning:focus {
    outline: 2px solid #F59E0B;
    outline-offset: 2px;
    box-shadow: 0 0 0 4px rgba(245, 158, 11, 0.2);
}

.btn-info {
    background: #3B82F6;
    color: white;
}

.btn-info:hover {
    background: #2563EB;
}

.btn-info:focus {
    outline: 2px solid #3B82F6;
    outline-offset: 2px;
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2);
}
```

#### Button Sizes
```css
.btn-large {
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    height: 48px;
    min-height: 48px;
    min-width: 48px;
}

.btn-small {
    padding: 0.375rem 0.75rem;
    font-size: 0.8125rem;
    height: 36px;
    min-height: 36px;
    min-width: 36px;
}
```

### Cards (卡片)
```css
.card {
    background: #FFFFFF;
    border-radius: 0.75rem;
    padding: 1.5rem;
    border: 1px solid #E2E8F0;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    transition: all 150ms;
}

.card:hover {
    border-color: #6366F1;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
```

### Inputs (输入框)
```css
.input-field {
    padding: 0.625rem 1rem;
    border: 1px solid #E2E8F0;
    border-radius: 0.5rem;
    font-size: 1rem;
    background: #FFFFFF;
    transition: all 150ms;
}

.input-field:focus {
    outline: none;
    border-color: #6366F1;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.input-field::placeholder {
    color: #94A3B8;
}
```

### Navigation (导航)
```css
.nav-link {
    color: #475569;
    text-decoration: none;
    font-weight: 500;
    transition: color 150ms;
    position: relative;
    cursor: pointer;
}

.nav-link:hover {
    color: #6366F1;
}

.nav-link.active {
    color: #6366F1;
}

.nav-link.active::after {
    content: '';
    position: absolute;
    bottom: -0.5rem;
    left: 0;
    right: 0;
    height: 2px;
    background: #6366F1;
}

.nav-link:focus {
    outline: 2px solid #6366F1;
    outline-offset: 2px;
    border-radius: 0.375rem;
}
```

### Status Badges (状态标签)
```css
.badge {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
}

.badge-success {
    background: rgba(16, 185, 129, 0.1);
    color: #10B981;
}

.badge-danger {
    background: rgba(239, 68, 68, 0.1);
    color: #EF4444;
}

.badge-warning {
    background: rgba(245, 158, 11, 0.1);
    color: #F59E0B;
}

.badge-info {
    background: rgba(59, 130, 246, 0.1);
    color: #3B82F6;
}
```

### Loading States (加载状态)
```css
.loading {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    color: #475569;
}

.loading-spinner {
    width: 20px;
    height: 20px;
    border: 2px solid #E2E8F0;
    border-top-color: #6366F1;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@media (prefers-reduced-motion: reduce) {
    .loading-spinner {
        animation: none;
    }
}
```

### Empty States (空状态)
```css
.empty-state {
    text-align: center;
    padding: 3rem 1.5rem;
    color: #94A3B8;
}

.empty-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    opacity: 0.5;
}

.empty-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: #475569;
    margin-bottom: 0.5rem;
}

.empty-description {
    font-size: 0.875rem;
    color: #94A3B8;
}
```

## 响应式断点

```css
/* Mobile (375px) */
@media (max-width: 375px) {
    .container {
        padding: 0 0.5rem;
    }
    
    .header-content {
        flex-direction: column;
        gap: 1rem;
    }
    
    .nav {
        flex-wrap: wrap;
        justify-content: center;
        gap: 0.5rem;
    }
    
    .btn {
        width: 100%;
    }
}

/* Tablet (768px) */
@media (max-width: 768px) {
    .features {
        grid-template-columns: 1fr;
    }
    
    .section-header {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .qa-options {
        flex-direction: column;
    }
}

/* Laptop (1024px) */
@media (max-width: 1024px) {
    .container {
        padding: 0 0.75rem;
    }
}

/* Desktop (1440px) */
@media (min-width: 1440px) {
    .container {
        max-width: 1440px;
    }
}
```

## 可访问性要求

### 键盘导航
- 所有交互元素必须可通过键盘访问
- Focus 状态必须清晰可见
- Tab 键顺序逻辑合理

### 屏幕阅读器
- 使用语义化 HTML 标签
- 添加适当的 ARIA 标签
- 提供描述性文本

### 对比度
- 文本对比度至少 4.5:1
- 大文本至少 3:1
- 交互元素对比度至少 3:1

### 触摸目标
- 最小触摸目标 44x44px
- 按钮和链接有足够的点击区域

### 减少动画
- 支持 prefers-reduced-motion
- 动画时长 150-300ms
- 避免闪烁和快速移动

## 性能要求

### CSS 优化
- 使用 CSS 变量
- 避免重复代码
- 使用高效的布局方式（Grid、Flexbox）

### 动画性能
- 使用 transform 和 opacity
- 避免触发重排
- 使用 will-change 优化

### 资源优化
- 字体预加载
- 图标使用 SVG
- 避免大图片

## 设计原则

### 1. 清晰的视觉层次
- 使用大小、颜色、间距建立层次
- 重要信息突出显示
- 次要信息弱化处理

### 2. 一致性
- 统一的间距和尺寸
- 一致的颜色使用
- 标准化的交互模式

### 3. 反馈
- 即时的视觉反馈
- 清晰的状态指示
- 明确的错误提示

### 4. 效率
- 快速的交互响应
- 最小化操作步骤
- 智能默认值

### 5. 专业性
- 干净的界面
- 精确的排版
- 适当的留白
