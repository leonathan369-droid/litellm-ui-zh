# LiteLLM 兼容性记录

本页区分“人工验证”和“真实环境自动化验证”，避免把“安装成功”误写成“所有页面都已人工确认”。

## 状态定义

- **VERIFIED**：维护者完成安装、完整性检查，并按定义范围进行人工浏览器确认。
- **AUTOMATED_VERIFIED**：真实 LiteLLM 精确版本完成安装、启动、Overlay 注入与浏览器级 smoke test，但尚未完成定义范围内的人工逐页检查。
- **UNVERIFIED**：尚无足够证据确认当前版本。
- **UNKNOWN**：无法取得可靠版本或状态数据。

## 当前记录

| LiteLLM | 系统 | 日期 | 状态 | 范围 |
| --- | --- | --- | --- | --- |
| 1.99.0 | macOS | 2026-09-03 | VERIFIED | 安装器、check、真实浏览器常用管理界面人工检查 |
| 1.101.0 | Ubuntu + macOS | 2026-09-18 | AUTOMATED_VERIFIED | 精确包安装、packaged UI 定位、overlay install/check/diagnose、LiteLLM 启动、/ui/ 注入、served overlay checksum；Linux 额外执行 Chromium 语言切换 smoke test |

v1.101.0 目前**没有**被标成 VERIFIED，因为还缺少登录后的核心管理路由逐页人工视觉检查。自动化成功并不等于翻译覆盖完整。

## 新版本验证流程

1. 等待 LiteLLM stable release；RC/dev/nightly 不作为兼容发布目标。
2. 创建兼容分支并安装精确版本。
3. 运行 `install.py upgrade/check/diagnose`。
4. 运行 `scripts/collect_strings.py` 收集静态 HTML 新候选英文。
5. 运行完整 CI 与真实 LiteLLM compatibility workflow。
6. 人工检查核心路由：Dashboard、Virtual Keys、Models + Endpoints、Playground、Usage、Agents、Skills、MCP Servers、Guardrails、Policies、Teams、Internal Users、Budgets、Logs、Settings。
7. 无法进入或依赖 Enterprise/数据库的页面必须标记 NOT TESTED，而不是 VERIFIED。
8. 更新 `compatibility/upstream.json` 与本页后才能发布兼容声明。

## 本地自测

```bash
python3 scripts/install.py upgrade --target "$HOME/.config/litellm/ui-zh"
python3 scripts/install.py check --target "$HOME/.config/litellm/ui-zh"
python3 scripts/install.py diagnose --target "$HOME/.config/litellm/ui-zh"
```

提交兼容性 Issue 时不要包含 API Key、MASTER_KEY、Cookie、数据库 URL、完整配置、请求内容或未脱敏日志。
