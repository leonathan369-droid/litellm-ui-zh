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
