# Architecture

## 目标

本项目保持为 LiteLLM WebUI 的轻量简体中文 Overlay，而不是 LiteLLM fork。

核心原则：

1. 不修改 LiteLLM Python 安装包。
2. 不改变 Proxy API、路由、数据库、密钥或计费行为。
3. 使用 LiteLLM 支持的 `LITELLM_UI_PATH` 提供独立静态 UI。
4. 安装和升级先在 staging 中完成并验证，再原子替换。
5. 翻译层不得污染模型名、项目名、日志文本或其他用户数据。

## 构建

```text
locales/zh-CN.json
        +
src/overlay.js
        |
scripts/build_patch.py
        v
dist/litellm-zh.js
```

`dist` 是可重复构建产物，CI 会重新构建并确认内容一致。

## 翻译策略

默认使用 exact-match。前后空白可保留，但普通词条不会作为任意子串替换。

动态 DOM 状态使用 WeakMap 保存当前 source 与 translated 值。当 React 修改已有 TextNode 或 `aria-label` / `placeholder` / `title` 时，新值会成为新的 source，因此切回英文不会恢复第一次出现的旧内容。

以下区域默认跳过：

- `script/style/noscript`
- `textarea/input/select/option` 的文本节点
- `pre/code`
- `contenteditable`
- 带 `data-litellm-zh-ignore` 的元素及子树
- 普通表格数据单元格（`td`）中的文本和可翻译属性；单元格内明确的按钮/标签仍可翻译

## 安装器安全模型

`install` 只写入不存在的目标目录。`upgrade` 不使用 `--force`，而是：

```text
current target
new LiteLLM packaged UI
        |
     staging
        |
copy + inject + manifest + verify
        |
old target -> backup
staging    -> target
```

失败时保留当前可用版本或执行回滚。

## 完整性与兼容性分离

`check` 分开报告：

- Overlay 文件完整性。
- 安装时 LiteLLM 来源版本与当前版本是否一致。
- 当前 LiteLLM 是否存在 VERIFIED / AUTOMATED_VERIFIED 记录。

“checksum 正常”不等于“当前 LiteLLM 已验证兼容”。

## 静态候选英文门禁

`scripts/collect_strings.py` 会扫描 LiteLLM 导出的 HTML 文本与可翻译属性。兼容性 CI 将结果与 `compatibility/static-unknown-allowlist.json` 对比；出现新的未翻译静态候选会直接失败，必须由维护者判断是新增翻译还是明确允许保留的品牌/标题。
