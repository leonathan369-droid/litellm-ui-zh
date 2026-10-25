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
| 1.106.3 | Ubuntu | 2026-10-25 | AUTOMATED_VERIFIED | 精确包安装、56 个静态 UI 路由、Overlay 注入与校验和、Chromium 标题翻译和路由更新恢复、中英文切换、动态词条与用户数据保护 |

LiteLLM 1.106.3 的版本级状态记为 **AUTOMATED_VERIFIED**；已在真实 Linux 环境完成精确包安装、Overlay 检查和 Chromium smoke。19 个登录后的 Admin UI 核心路由检查属于自动适配流程的额外合并门槛，本次本地检查没有数据库服务，因此没有把该结果写入本版本范围。人工逐页检查仍以仓库明确记录的平台为范围，不会把自动化结果写成 VERIFIED。

## 新版本自动维护

`upstream-watch.yml` 每天检查 LiteLLM 最新 stable release。发现高于最新自动验证版本后，Codex 会读取经 PyPI SHA256 校验的精确 wheel 静态 UI，按上游 UI 变化更新翻译，并创建兼容 PR。工作流随后针对该 PR 分支运行仓库测试、精确版本 UI/Chromium smoke test，以及 PostgreSQL 支撑的 19 个 Admin UI 核心路由检查，并维护经核验的静态路由清单。纯翻译更新在全部检查通过后自动合并；如果 Overlay 逻辑、未知词条白名单或上游路由发生变化，工作流会保留 PR 并要求人工审查。其他失败也会保留 PR，并创建带有工作流链接的问题。

自动翻译需要在 GitHub Actions Secrets 中设置 `OPENAI_API_KEY`。仓库设置还需允许 Actions 创建 PR；现有分支保护规则仍会生效。首次启用时，需先通过仓库正常审查流程合并这套工作流；之后 GitHub Actions 才能按分支调度新版本的验证工作流。

## 本地自测

```bash
python3 scripts/install.py upgrade --target "$HOME/.config/litellm/ui-zh"
python3 scripts/install.py check --target "$HOME/.config/litellm/ui-zh"
python3 scripts/install.py diagnose --target "$HOME/.config/litellm/ui-zh"
```

提交兼容性 Issue 时不要包含 API Key、MASTER_KEY、Cookie、数据库 URL、完整配置、请求内容或未脱敏日志。
