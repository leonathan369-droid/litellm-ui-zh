# LiteLLM 兼容性记录

本页区分“人工验证”和“真实环境自动化验证”，避免把“安装成功”误写成“所有平台、所有页面都已人工确认”。

## 状态定义

- **VERIFIED**：维护者在对应系统上完成安装、完整性检查，并按定义范围进行人工浏览器确认。
- **AUTOMATED_VERIFIED**：真实 LiteLLM 精确版本完成安装、启动、Overlay 注入与浏览器级自动化验证；若不同系统的人工覆盖不一致，版本级状态保持保守。
- **UNVERIFIED**：尚无足够证据确认当前版本。
- **UNKNOWN**：无法取得可靠版本或状态数据。

## 当前记录

| LiteLLM | 系统 | 日期 | 状态 | 范围 |
| --- | --- | --- | --- | --- |
| 1.99.0 | macOS | 2026-09-03 | VERIFIED | 安装器、check、真实浏览器常用管理界面人工检查 |
| 1.101.0 | Ubuntu | 2026-09-20 | 人工路由复核完成；版本级状态保持 AUTOMATED_VERIFIED | 精确包安装、PostgreSQL/Prisma 初始化、真实 Admin UI 登录、15 个核心管理路由、关键 placeholder 回归断言、全页截图人工复核 |
| 1.101.0 | macOS | 2026-09-20 | AUTOMATED_VERIFIED | 精确包安装、packaged UI 定位、overlay install/check/diagnose、LiteLLM 启动、/ui/ 注入与 served overlay checksum |

LiteLLM 1.101.0 的版本级状态仍记为 **AUTOMATED_VERIFIED**，原因是当前逐页人工视觉复核是在 Ubuntu/Linux Chromium 环境完成的；macOS 已通过真实包兼容自动化，但没有宣称完成同等范围的逐页人工检查。这样 `check` 不会把某一平台的人工结果误报成所有平台均 VERIFIED。

## LiteLLM 1.105.1 本地验证（2026-10-15）

状态为 **AUTOMATED_VERIFIED，仅 Ubuntu**。使用 Ubuntu 26.04、Python 3.12、独立 PostgreSQL 18、Prisma 0.15.0 和 Google Chrome；未连接生产数据库或真实模型供应商。

- 精确包安装、独立 UI 副本 install/upgrade/check/diagnose、55 个 HTML 路由注入通过；实际提供的 JS 与构建产物一致，原始包内 772 个 UI 文件仍与 wheel RECORD 哈希一致。
- 21 项 Python 测试和 9 项 JavaScript 测试通过，生成产物可重复构建；静态候选扫描没有新增未审核英文。
- 真实管理员登录和上述 15 个核心路由检查通过，每页执行中文→英文→中文切换，关键 placeholder 断言通过，没有浏览器 pageerror。
- 初始外挂曾因提前翻译 SSR 加载文字触发 React #418；关闭外挂的对照页无错误。延迟到原加载容器被 React 移除后初始化，真实浏览器对照复验错误消失。另修复动态属性绕过数据保护和切换按钮被移除后无法恢复。
- 检查了模型与管理员设置页截图；这不是所有页面、所有弹窗和 CRUD 操作的完整人工验收。该轮未测试 macOS、付费 Enterprise 功能、真实模型调用或生产自定义插件；策略模板、业务数据、品牌和技术标识允许保持原文。
- CI 工作流已更新为 1.105.1；本记录依据本地验证，不把未执行的 GitHub Actions 或 macOS 工作流写为通过。

## 新版本验证流程

1. 等待 LiteLLM stable release；RC/dev/nightly 不作为兼容发布目标。
2. 创建兼容分支并安装精确版本。
3. 运行 `install.py upgrade/check/diagnose`。
4. 运行 `scripts/collect_strings.py` 收集静态 HTML 新候选英文。
5. 运行完整 CI、真实 LiteLLM compatibility workflow 与数据库支持的 Admin UI route review。
6. 人工检查核心路由：Virtual Keys、Models + Endpoints、Playground、Usage、Agents、Skills、MCP Servers、Guardrails、Policies、Teams、Internal Users、Budgets、Logs、Router Settings、Admin Settings。
7. 无法进入或依赖 Enterprise/外部 Provider 的页面必须标记 NOT TESTED，而不是 VERIFIED。
8. 更新 `compatibility/upstream.json` 与本页后才能发布兼容声明。

## 本地自测

```bash
python3 scripts/install.py upgrade --target "$HOME/.config/litellm/ui-zh"
python3 scripts/install.py check --target "$HOME/.config/litellm/ui-zh"
python3 scripts/install.py diagnose --target "$HOME/.config/litellm/ui-zh"
```

提交兼容性 Issue 时不要包含 API Key、MASTER_KEY、Cookie、数据库 URL、完整配置、请求内容或未脱敏日志。


### Ubuntu 生产补充验证（2026-10-15）

在自有生产环境部署同一份外挂（代码提交 `38f0bbd935fadba5333500abd303d7ffe4bf5eb7`），LiteLLM 保持 1.105.1。应用侧发布工具从安装包复制独立 UI 并注入外挂；这项结果验证运行时外挂，不代表在该生产环境运行了本仓库安装器。

- 55 个 HTML 路由注入完成，线上 JS 校验和与构建产物一致，官方包中的 HTML 未修改。
- 真实 HTTPS 管理登录 API、中文登录页面、15 个核心管理路由以及每页中英切换通过；Chromium `pageerror` 为 0。
- 模型与 Team 名称保持原文；从原生菜单打开自定义费用报表 iframe，原生短期身份交换及报表加载成功。
- 模型、Team、业务 Key 配置与报表文件在部署前后摘要一致；服务无异常重启。
- 仍为 `AUTOMATED_VERIFIED`：不扩大到 macOS、全部 CRUD、Enterprise 功能、其他自定义插件或真实厂商调用。生产截图、凭据和业务数据不提交到本仓库。


### 1.105.1 固定界面文案补齐（2026-10-15）

本轮针对 Lens 未翻译的问题扩展到管理界面固定文案，词典从 739 条增加至 6,100 条（新增 5,361 条）。补齐范围包含主页面、详情、弹窗、空态、表单、条件按钮、提示、无障碍标签及独立的固定文本片段；保留现有精确匹配与数据保护机制，不修改 LiteLLM 或翻译运行时代码。

静态核查使用与部署包逐文件哈希一致的 1.105.1 官方 HTML/JS。分模块交叉评审修正了配置“键名”和延迟缓冲百分比的译法；代码、模型标识、URL 和技术参数保持原样。词条数量不是全部页面或功能完整覆盖的证明。

明确保留边界：服务器返回的策略模板/业务内容、模型与项目名称不做泛化翻译；含日期的完整动态拼接句（例如模型洞察时间范围、累计节省时间段）仍可能为英文。未加入通配替换，未执行真实厂商推理、OAuth/worker 接入、付费 Enterprise 功能或全量 CRUD。

本轮验证（40 页检查后追加 9 个组合标签，再针对智能体、技能、MCP 页面复验，并重新验证完整词典往返）：

- 21 项 Python 测试、11 项 JavaScript 测试、构建可重复性与语法检查通过。
- 隔离 PostgreSQL 支持的 LiteLLM 1.105.1 中，以专用测试管理员会话访问 40 个页面，逐页中文→英文→中文切换，JavaScript pageerror 为 0；另打开新建密钥、团队、预算、智能体、技能、搜索工具、MCP 服务器、访问组和标签等弹窗（不提交）。Lens 截图人工检查通过。
- Chromium 真实 DOM 对全部 6,100 条词条验证中文显示及英文精确恢复；同名数据单元格、代码、输入值和独立 iframe 内容保持原文。它验证匹配/恢复机制，不证明所有页面分支均已人工验收。
- 最终资源 SHA256：`59d4af30c3b80e5de254e224e48caa78abf942f444ec4aa3e0acc0673c286adb`。浏览器正常关闭并验证退出。
- 本轮浏览器证据来自本地隔离环境，不代表已完成生产登录浏览器验收；生产交付和 HTTP 检查由使用方仓库单独记录。
