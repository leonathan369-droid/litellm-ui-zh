# Maintainer SOP

AI 按 [litellm-ui-zh-maintain skill](../.agents/skills/litellm-ui-zh-maintain/SKILL.md) 判断任务范围与步骤，本页维护执行入口和检查项。

## 1. 发现新 stable release

`upstream-watch.yml` 每天检查 BerriAI/litellm 最新 stable release。它以 `latest_verified` 与 `latest_automated_verified` 中已审查到的最高版本作为发现基线，只有出现更高 stable 版本才创建兼容性 Issue。自动化只负责发现任务，不自动标记兼容或发布。

## 2. 核对分支与目标版本

默认在当前分支工作，只有用户明确要求时才新建分支；兼容分支可命名为：

```text
compat/vX.Y.Z
```

目标必须是精确 LiteLLM stable 版本；RC/dev/nightly 不作为兼容发布目标。

Git `upstream` 是汉化 Overlay 的来源仓库，`BerriAI/litellm` 是被适配的官方软件，二者独立。同步汉化上游前核对 `git remote -v`、工作树与提交差异，按已授权范围合入并保留本地 fork 的修复；同步不自动触发版本升级、tag、Release 或网关部署。

## 3. 基础检查

```bash
python3 scripts/build_patch.py --check
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/install.py scripts/build_patch.py scripts/check_upstream.py scripts/collect_strings.py
node --check dist/litellm-zh.js
node --test tests/test_translation.js
```

## 4. 真实 LiteLLM 验证

在本任务独立 Python 环境安装目标精确版本后，首次使用不存在的测试目录：

```bash
python3 scripts/install.py install --python /path/to/test-venv/bin/python --target /path/to/test-ui
```

仅对本任务已创建的测试目录验证升级；各命令都指定同一个目标 Python，防止来源版本判断落到其他环境：

```bash
python3 scripts/install.py upgrade --python /path/to/test-venv/bin/python --target /path/to/test-ui
python3 scripts/install.py check --python /path/to/test-venv/bin/python --target /path/to/test-ui
python3 scripts/install.py diagnose --python /path/to/test-venv/bin/python --target /path/to/test-ui
python3 scripts/collect_strings.py /path/to/test-ui --json
```

`compatibility.yml` 还会在 Ubuntu/macOS 安装精确 LiteLLM、定位真实 packaged UI、启动 LiteLLM、确认 `/ui/` 已注入 Overlay，并校验实际服务出来的 JS 与安装目录一致。Linux runner 额外执行 Chromium smoke test，验证 Overlay 加载和中/EN 切换。`admin-ui-route-review.yml` 使用 PostgreSQL + Prisma 启动真实 Admin UI 会话，登录后逐页检查核心路由、关键中文 placeholder，并保存截图供人工复核。

本地复用登录后路由检查时，先按目标版本在隔离数据库启动 LiteLLM，并注入 Overlay；再运行目标 Python 环境中的 `tests/admin_ui_route_review.py`。该脚本读取 `LITELLM_TEST_BASE_URL`、`UI_USERNAME`、`UI_PASSWORD` 和 `RUNNER_TEMP`，结果写入 `RUNNER_TEMP/admin-routes/`。地址必须显式指向本任务实例，凭据仅使用隔离测试账号，输出目录使用本任务专属目录；脚本会输出页面正文预览和截图，只使用虚构业务数据，不能直接用于生产。不得把 CI 中的 `prisma db push --accept-data-loss` 用于已有业务库。脚本的固定视口和 15 条路由只证明对应自动化范围；真实版本新增页面、弹窗和人工视觉验收需单独覆盖。运行前核对目标版本登录流程与路由，不能仅因未回到登录页就认定目标页面已打开。

静态英文门禁复用 [.github/workflows/compatibility.yml](../.github/workflows/compatibility.yml) 中的差集检查：将收集结果 `unknown` 与 `compatibility/static-unknown-allowlist.json` 的 `allowed` 比较，差集非空则失败并逐项审核。`collect_strings.py` 仅负责收集，不会因为发现未知英文而返回失败。

## 5. 翻译维护

普通翻译优先只改：

```text
locales/zh-CN.json
```

然后运行：

```bash
python3 scripts/build_patch.py
python3 scripts/build_patch.py --check
```

不要直接手改 `dist/litellm-zh.js`。

`collect_strings.py` 只扫描渲染后的 HTML 文本和可翻译属性，是候选收集器，不是完整覆盖证明。运行时 JS 才出现的字符串仍依赖浏览器检查。

## 6. 人工浏览器检查

核心路由至少包括：

- Dashboard
- Virtual Keys
- Models + Endpoints
- Playground
- Usage
- Agents
- Skills
- MCP Servers
- Guardrails
- Policies
- Teams
- Internal Users
- Budgets
- Logs
- Settings

检查：

- 新增英文与错误翻译。
- 中文布局溢出或错位。
- 模型名、项目名、日志、代码等用户数据是否被误翻。
- 中/EN 多次切换是否恢复当前英文。
- 动态弹窗、placeholder、aria-label 是否跟随更新。

## 7. 状态升级

真实安装、服务和浏览器 smoke CI 通过，但人工逐页检查未完成：记录 `automated-verified`。

人工检查范围完成后：改为 `verified`。

无法进入或依赖 Enterprise/数据库的页面明确记录 NOT TESTED。

## 8. Release checklist

- [ ] locale JSON 合法
- [ ] dist 可重复构建
- [ ] Python tests 全绿
- [ ] JS tests 全绿
- [ ] Ubuntu CI 全绿
- [ ] macOS CI 全绿
- [ ] install/upgrade/restore/rollback 测试全绿
- [ ] compatibility workflow 全绿
- [ ] unknown strings 已审核
- [ ] 核心浏览器路由已人工检查或明确记录未完成
- [ ] compatibility/upstream.json 已更新
- [ ] docs/compatibility.md 已更新
- [ ] CHANGELOG 已更新
- [ ] README 版本说明已更新
- [ ] 创建 tag 和 GitHub Release

所有门槛满足前，不自动把新版本标记为 VERIFIED，也不自动发布。
