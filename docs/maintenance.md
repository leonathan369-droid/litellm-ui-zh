# Maintainer SOP

## 1. 发现新 stable release

`upstream-watch.yml` 每天检查 BerriAI/litellm 最新 stable release。它以 `latest_verified` 与 `latest_automated_verified` 中已审查到的最高版本作为发现基线，只有出现更高 stable 版本才创建兼容性 Issue。自动化只负责发现任务，不自动标记兼容或发布。

## 2. 建兼容分支

建议命名：

```text
compat/vX.Y.Z
```

目标必须是精确 LiteLLM stable 版本；RC/dev/nightly 不作为兼容发布目标。

## 3. 基础检查

```bash
python3 scripts/build_patch.py --check
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/install.py scripts/build_patch.py scripts/check_upstream.py scripts/collect_strings.py
node --check dist/litellm-zh.js
node --test tests/test_translation.js
```

## 4. 真实 LiteLLM 验证

安装目标精确版本后：

```bash
python3 scripts/install.py upgrade --target /path/to/test-ui
python3 scripts/install.py check --target /path/to/test-ui
python3 scripts/install.py diagnose --target /path/to/test-ui
python3 scripts/collect_strings.py /path/to/test-ui --json
```

`compatibility.yml` 还会在 Ubuntu/macOS 安装精确 LiteLLM、定位真实 packaged UI、启动 LiteLLM、确认 `/ui/` 已注入 Overlay，并校验实际服务出来的 JS 与安装目录一致。Linux runner 额外执行 Chromium smoke test，验证 Overlay 加载和中/EN 切换。`admin-ui-route-review.yml` 使用 PostgreSQL + Prisma 启动真实 Admin UI 会话，登录后逐页检查核心路由、关键中文 placeholder，并保存截图供人工复核。

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
