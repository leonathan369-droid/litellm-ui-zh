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
- 检查了模型与管理员设置页截图；这不是所有页面、所有弹窗和 CRUD 操作的完整人工验收。未测试 macOS、付费 Enterprise 功能、真实模型调用或生产自定义插件；策略模板、业务数据、品牌和技术标识允许保持原文。
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
