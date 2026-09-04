# LiteLLM WebUI 简体中文补丁 v0.1.1：发布文案包

本文件用于人工发布前审核。三版文案均只基于仓库已验证事实：本项目是非官方浏览器端
简体中文覆盖层；不修改 LiteLLM Python 安装包。当前补丁发布版本为 `v0.1.1`，已在
macOS 的 LiteLLM `v1.99.0` 上完成安装、`check` 和真实浏览器界面检查。未列出的系统、
浏览器和 LiteLLM 版本均不作兼容性承诺。

发布时使用仓库中的脱敏预览图 `docs/assets/litellm-ui-zh-preview.png`。不得附带终端
历史、环境变量、管理后台数据、密钥、请求、用量、日志或未脱敏截图。

## 版本 A：GitHub Discussion

**适用位置：** 本仓库的 GitHub Discussion，使用 `Announcements` 分类。
已于 2026-09-04 发布为 [Discussion #1](https://github.com/leonathan369-droid/litellm-ui-zh/discussions/1)。

**标题：** LiteLLM WebUI 简体中文补丁：不修改安装包，可校验和回退

~~~~markdown
给自部署 LiteLLM 的中文用户做了一个非官方 WebUI 简体中文覆盖层：
https://github.com/leonathan369-droid/litellm-ui-zh

版本信息：补丁 `v0.1.1`；已验证 LiteLLM `v1.99.0`（macOS）。

它不会修改 LiteLLM 的 Python 安装包。安装器会复制原始静态 UI 到独立目录、注入翻译
脚本，并提供 `check` 校验和 `restore` 回退；Proxy API、模型路由、数据库、密钥和计费
行为不在补丁修改范围内。

快速开始：

```zsh
git clone https://github.com/leonathan369-droid/litellm-ui-zh.git
cd litellm-ui-zh
python3 scripts/install.py install --target "$HOME/.config/litellm/ui-zh"
python3 scripts/install.py check --target "$HOME/.config/litellm/ui-zh"
```

目前已验证 macOS + LiteLLM `v1.99.0`：安装器完成 51 个 HTML 路由注入，`check` 通过，
并在真实浏览器中检查中文覆盖层。其他版本欢迎补充兼容性反馈：
https://github.com/leonathan369-droid/litellm-ui-zh/blob/main/docs/compatibility.md

这是社区补丁，不是 LiteLLM 官方发布。请不要在 Issue 中提交 API Key、`MASTER_KEY`、
Cookie、数据库 URL、完整配置或未脱敏日志。觉得有帮助的话，欢迎点个 Star；翻译、安装
或兼容性问题都欢迎通过 Issue 反馈。
~~~~

## 版本 B：V2 / Linux.do 技术社区

**建议标题：** 给 LiteLLM WebUI 做了个简中补丁：不改安装包，支持校验和回退

**建议标签：** `开源`、`自部署`、`AI`、`LiteLLM`；按实际社区可选标签发布，不强行堆砌。

~~~~markdown
自部署 LiteLLM 时，WebUI 里不少管理页面还是英文。我做了一个非官方简体中文覆盖层：
https://github.com/leonathan369-droid/litellm-ui-zh

版本信息：补丁 `v0.1.1`；已验证 LiteLLM `v1.99.0`（macOS）。

核心思路是不直接改 LiteLLM 安装包：安装器把它自带的静态 UI 复制到单独目录，再注入
翻译脚本。这样更新时可重新安装，出了问题也能 `check` 校验或 `restore` 回退，补丁不改
Proxy API、模型路由、数据库、密钥和计费逻辑。

安装：

```zsh
git clone https://github.com/leonathan369-droid/litellm-ui-zh.git
cd litellm-ui-zh
python3 scripts/install.py install --target "$HOME/.config/litellm/ui-zh"
python3 scripts/install.py check --target "$HOME/.config/litellm/ui-zh"
```

然后在启动 LiteLLM 的服务环境设置：

```zsh
export LITELLM_UI_PATH="$HOME/.config/litellm/ui-zh"
```

目前只实际验证了 macOS + LiteLLM `v1.99.0`：51 个 HTML 路由完成注入，`check` 通过，
浏览器内已手动检查。Linux、Windows 和其他 LiteLLM 版本还没有承诺，欢迎按兼容性模板
反馈：
https://github.com/leonathan369-droid/litellm-ui-zh/blob/main/docs/compatibility.md

可以附一张仓库里的脱敏界面预览图。请勿在评论或 Issue 中贴密钥、私有地址、配置或日志。
觉得有用欢迎点个 Star；未翻译文本、安装问题和版本兼容性问题都欢迎提 Issue。
~~~~

## 版本 C：掘金 / 知乎教程帖

**建议标题：** LiteLLM WebUI 中文化：为什么不直接改安装包，以及如何校验与回退

**摘要：** 用独立 UI 目录承载 LiteLLM WebUI 的简体中文覆盖层，避免修改 Python 安装包；
给出安装、校验、回退和升级验证步骤，并明确当前兼容性边界。

~~~~markdown
LiteLLM Proxy 的 WebUI 可用于模型、路由、密钥和用量等管理。对中文用户来说，管理页
里仍有大量英文文本；但直接改 `site-packages` 里的静态文件会让升级、排错和回退变得很
难追踪。

我做了一个非官方的简体中文覆盖层：
https://github.com/leonathan369-droid/litellm-ui-zh

版本信息：补丁 `v0.1.1`；已验证 LiteLLM `v1.99.0`（macOS）。

它的做法是把 LiteLLM 自带的静态 UI 复制到独立目录，然后在这个副本里注入浏览器端翻译
脚本。LiteLLM Python 包不被改动，Proxy API、模型路由、数据库、密钥和计费逻辑也不在
补丁作用范围内。

## 安装

```zsh
git clone https://github.com/leonathan369-droid/litellm-ui-zh.git
cd litellm-ui-zh
python3 scripts/install.py install --target "$HOME/.config/litellm/ui-zh"
```

让启动 LiteLLM 的服务环境使用这个目录：

```zsh
export LITELLM_UI_PATH="$HOME/.config/litellm/ui-zh"
```

重启 LiteLLM 后，右下角可以在 `中 / EN` 间切换。请只在不含密钥、请求、用量、日志或
业务数据的页面截图分享。

## 为什么要校验

LiteLLM 升级后，静态 UI 的页面结构可能变化。升级前保留当前 UI 目录；升级后重新安装并
执行：

```zsh
python3 scripts/install.py check --target "$HOME/.config/litellm/ui-zh"
```

该命令会检查自定义目录中的翻译脚本和 HTML 路由注入状态。若需要恢复该目录的原始 UI，
可以执行：

```zsh
python3 scripts/install.py restore --target "$HOME/.config/litellm/ui-zh"
```

## 当前验证范围

当前补丁版本为 `v0.1.1`，且仅验证 macOS + LiteLLM `v1.99.0`：安装器完成 51 个 HTML
路由注入，`check` 通过，
并手动检查了真实浏览器界面。Linux、Windows 和其他 LiteLLM 版本仍待验证，详细记录：
https://github.com/leonathan369-droid/litellm-ui-zh/blob/main/docs/compatibility.md

这是社区补丁，不是 LiteLLM 官方发布。项目有帮助欢迎点个 Star；翻译建议、安装问题或
兼容性报告请通过 Issue 提交。提交前务必脱敏，勿公开 API Key、`MASTER_KEY`、Cookie、
数据库 URL、完整配置和未脱敏日志。
~~~~

## 发布前核对

| 项目 | 当前结论 | 发布动作 |
| --- | --- | --- |
| 版本标注 | 三版均标明补丁 `v0.1.1` 与 `macOS + LiteLLM v1.99.0` 已验证 | 不增加“全平台”“完全兼容”“官方”表述 |
| 图片 | 预览图已人工审查为脱敏的真实空状态页面 | 仅使用 `docs/assets/litellm-ui-zh-preview.png` |
| 反馈入口 | 已有翻译、安装、兼容性 Issue 表单 | 只链接仓库 Issue，不要求用户在帖子中贴诊断 |
| GitHub Discussion | 已启用；版本 A 已在 `Announcements` 发布为 [Discussion #1](https://github.com/leonathan369-droid/litellm-ui-zh/discussions/1) | 观察反馈并维护该公告；不以 Issue 替代 |
| V2 / Linux.do | 需使用账号页面发布 | 选择一个社区先发版本 B，配图最多一张 |
| 掘金 / 知乎 | 需使用账号页面发布 | 在前两类社区获得基础反馈后再发版本 C |
| 发布后互动 | 首日重点回答安装和兼容性问题 | 引导用户走脱敏 Issue；不承诺响应时限 |

## 建议顺序

1. 在仓库首页与 Release 保持当前 README、预览图和兼容性记录。
2. 版本 A 已在 GitHub Discussions 发布；观察反馈，必要时置顶或链接到仓库首页。
3. 选择 V2 或 Linux.do 中一个最熟悉的社区发布版本 B，观察 48 小时问题类型。
4. 根据真实反馈补充 FAQ 或兼容性记录，再发布版本 C，避免教程与仓库实际状态脱节。
