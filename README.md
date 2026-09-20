# LiteLLM WebUI 简体中文 Overlay

[![Verify](https://github.com/leonathan369-droid/litellm-ui-zh/actions/workflows/verify.yml/badge.svg)](https://github.com/leonathan369-droid/litellm-ui-zh/actions/workflows/verify.yml)
[![LiteLLM Compatibility](https://github.com/leonathan369-droid/litellm-ui-zh/actions/workflows/compatibility.yml/badge.svg)](https://github.com/leonathan369-droid/litellm-ui-zh/actions/workflows/compatibility.yml)
[![Release](https://img.shields.io/github/v/release/leonathan369-droid/litellm-ui-zh)](https://github.com/leonathan369-droid/litellm-ui-zh/releases)

这是一个独立的 LiteLLM Proxy WebUI 简体中文浏览器端 Overlay。它复制 LiteLLM 自带静态 UI 到独立目录，再注入翻译脚本；不修改 LiteLLM Python 包、API、模型路由、数据库、密钥或计费逻辑。

当前发布版本为 **v0.2.0**。LiteLLM **v1.101.0 / Ubuntu + macOS** 已完成精确包安装、启动、UI 注入和浏览器级自动化验证；其中 Ubuntu 还完成了 PostgreSQL 支撑的真实 Admin UI 登录、15 个核心管理路由检查与人工截图复核。为避免把 Ubuntu 的人工结果夸大到 macOS，版本级 `check` 状态仍保守记录为 `AUTOMATED_VERIFIED`。LiteLLM **v1.99.0 / macOS** 保留历史 `VERIFIED` 记录。完整范围见 [兼容性记录](docs/compatibility.md)。

## 快速安装

前提：已单独安装 LiteLLM，并且当前 Python 环境包含 LiteLLM WebUI。

```bash
git clone https://github.com/leonathan369-droid/litellm-ui-zh.git
cd litellm-ui-zh
python3 scripts/build_patch.py --check
python3 scripts/install.py install \
  --target "$HOME/.config/litellm/ui-zh"
```

让启动 LiteLLM 的同一环境使用该目录：

```bash
export LITELLM_UI_PATH="$HOME/.config/litellm/ui-zh"
litellm --host 127.0.0.1 --port 4000
```

如果 LiteLLM 在另一个虚拟环境中：

```bash
python3 scripts/install.py install \
  --python /path/to/litellm-venv/bin/python \
  --target "$HOME/.config/litellm/ui-zh"
```

## 升级

升级 LiteLLM 或更新本仓库后，使用：

```bash
python3 scripts/install.py upgrade \
  --target "$HOME/.config/litellm/ui-zh"
```

`upgrade` 会重新复制当前 LiteLLM 的原始 UI，在 staging 中注入最新版 Overlay、执行完整检查，再原子替换目标目录；旧版本会保留为备份。失败时不会用半成品覆盖当前可用目录。

## 检查与诊断

```bash
python3 scripts/install.py check --target "$HOME/.config/litellm/ui-zh"
python3 scripts/install.py diagnose --target "$HOME/.config/litellm/ui-zh"
```

兼容性状态：

- `VERIFIED`：完成维护者定义范围内的人工浏览器验证。
- `AUTOMATED_VERIFIED`：真实 LiteLLM 包安装、启动和浏览器级 smoke test 已通过，但尚未完成定义范围内的人工逐页检查。
- `UNVERIFIED`：该 LiteLLM 版本不在已验证记录中。
- `UNKNOWN`：无法安全取得版本或兼容记录。

`check` 同时区分“安装时的 LiteLLM 来源版本是否仍与当前版本一致”和“该版本是否经过兼容性验证”，不会把 checksum 正常误写成兼容已确认。

## 回退

```bash
python3 scripts/install.py restore \
  --target "$HOME/.config/litellm/ui-zh"
```

也可以移除 `LITELLM_UI_PATH` 并重启 LiteLLM，直接回到 LiteLLM 自带 WebUI。

## 翻译架构

- `locales/zh-CN.json`：翻译词典。
- `src/overlay.js`：DOM Overlay 运行时。
- `scripts/build_patch.py`：构建脚本。
- `dist/litellm-zh.js`：安装器实际使用的可重复构建产物。

默认只做**完整 UI 文本匹配**，不再对任意字符串执行短词子串替换，因此 `PageRank`、`UserService`、`All-MiniLM` 之类用户数据不会因为 `Page`、`User`、`All` 词条被污染。

动态 DOM 使用 WeakMap 记录当前 source/translated 状态；React 更新已有文本或 `aria-label` / `placeholder` / `title` 后，切回英文会恢复**当前**英文，而不是第一次出现的旧值。

Overlay 会跳过代码、预格式化文本、可编辑区域和显式标记 `data-litellm-zh-ignore` 的子树。

## 维护与贡献

维护 SOP 见 [docs/maintenance.md](docs/maintenance.md)，架构边界见 [docs/architecture.md](docs/architecture.md)。新 LiteLLM stable release 会由 GitHub Actions 自动发现并建立兼容性任务，但**不会自动标记兼容，也不会自动发布 Release**。

普通翻译优先只修改 `locales/zh-CN.json`，然后运行：

```bash
python3 scripts/build_patch.py
python3 scripts/build_patch.py --check
python3 -m unittest discover -s tests -v
node --test tests/test_translation.js
```

安全问题见 [SECURITY.md](SECURITY.md)，普通安装或翻译问题见 [SUPPORT.md](SUPPORT.md)。

## 范围与归属

本仓库不包含 LiteLLM 源码、原始 WebUI 静态包、生产配置或凭据。LiteLLM 是 BerriAI 维护的独立项目；本项目是社区维护的非官方中文 Overlay。详细归属见 [NOTICE.md](NOTICE.md)。
