# Network URL 画面比例调整 — 编码任务规划

## 1. CSS 选择器发现与分析

- [ ] 启动 Streamlit 应用（`streamlit run web/app.py`），在浏览器中打开应用页面
- [ ] 按 F12 打开浏览器开发者工具（DevTools），在 Elements 面板中搜索包含 "Local URL" 和 "Network URL" 文本的 DOM 节点
- [ ] 记录 Local URL 行元素和 Network URL 行元素的 CSS 类名、data-testid 属性及 DOM 层级结构
- [ ] 在 Computed 面板中对比 Local URL 和 Network URL 元素的 `font-size`、`line-height`、`margin`、`padding` 属性值，记录差异清单

## 2. CSS 覆盖规则编写与实时验证

- [ ] 在 DevTools 的 Styles 面板中，针对 Network URL 行元素临时添加 CSS 覆盖规则，将 `font-size` 对齐至 Local URL 的值
- [ ] 在 DevTools 中临时添加 `line-height` 覆盖规则，将 Network URL 行高对齐至 Local URL 的值
- [ ] 在 DevTools 中临时添加 `margin-top`、`margin-bottom`、`padding` 覆盖规则，将 Network URL 间距对齐至 Local URL 的值
- [ ] 肉眼对比 Local URL 和 Network URL 的画面比例，确认视觉上无差异；若仍有差异，继续调整其他相关 CSS 属性直至一致
- [ ] 将 DevTools 中验证通过的 CSS 规则整理为最终版 CSS 字符串，使用 `!important` 确保优先级

## 3. inject_custom_css() 函数实现与注入

- [ ] 在 `web/app.py` 中 `st.set_page_config(...)` 之后（L22 之后）、侧边栏代码之前，新增 `inject_custom_css()` 函数定义，包含 CSS 样式字符串和 `st.markdown(custom_css, unsafe_allow_html=True)` 注入逻辑
- [ ] 在 `st.set_page_config(...)` 之后、侧边栏代码之前，新增 `inject_custom_css()` 函数调用
- [ ] 确认 `inject_custom_css()` 的函数签名符合设计文档：`def inject_custom_css() -> None`
- [ ] 确认 CSS 注入内容不包含恶意代码，`unsafe_allow_html=True` 参数使用安全

## 4. 样式注入位置与执行顺序验证

- [ ] 确认 `inject_custom_css()` 在 `st.set_page_config()` 之后调用（Streamlit 要求 `set_page_config` 为首个命令）
- [ ] 确认 `inject_custom_css()` 在侧边栏和主界面渲染之前调用，确保样式在 URL 信息区域渲染时已生效
- [ ] 确认 `.streamlit/config.toml` 中 `headless = true` 配置保持不变

## 5. 验证与测试

- [ ] CSS 注入验证：启动应用后，在浏览器 DevTools 中确认自定义 CSS 规则已被加载到 DOM 中
- [ ] 样式属性验证：在 DevTools 的 Computed 面板中，对比 Local URL 和 Network URL 元素的 `font-size`、`line-height`、`margin`、`padding` 值，确认完全一致
- [ ] 视觉对比验证：肉眼观察 Local URL 和 Network URL 的画面比例，确认无差异
- [ ] URL 可访问性验证：点击 Local URL 和 Network URL 链接，确认均可正确跳转到对应地址
- [ ] URL 地址完整性验证：确认 Local URL 地址为 `http://localhost:{port}`，Network URL 地址为 `http://{ip}:{port}`，内容未被修改
- [ ] Local URL 样式不变验证：对比调整前后 Local URL 的显示效果，确认 Local URL 样式未被改变
- [ ] 移除回退验证：注释掉 `inject_custom_css()` 调用并重启应用，确认 URL 信息区域恢复为框架默认样式
- [ ] 跨浏览器验证：在 Chrome、Firefox、Edge 中分别验证样式效果一致
- [ ] 编码格式验证：确认修改后的 `web/app.py` 文件保存为 UTF-8 编码

## 6. 禁止修改位置确认

- [ ] 确认 `web/app.py` L16-21 的 `st.set_page_config(...)` 页面配置未被修改
- [ ] 确认 `web/app.py` 侧边栏代码（标题、工作流程、赛事信息）未被修改
- [ ] 确认 `web/app.py` 主界面代码（论文上传、执行等逻辑）未被修改
- [ ] 确认 `.streamlit/config.toml` 的 `[server] headless = true` 配置未被修改
