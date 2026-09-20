# LiteLLM WebUI 简体中文补丁 v0.2.0：不改安装包的中文界面方案

LiteLLM Proxy 的 WebUI 很适合做模型、路由、密钥和用量管理，但对中文用户而言，日常
操作时仍会遇到大量英文界面。这个仓库提供一个非官方的浏览器端简体中文覆盖层：它不
修改 LiteLLM 的 Python 安装包，也不改变 Proxy API、模型路由、数据库或计费行为。

当前补丁版本为 `v0.2.0`；LiteLLM `v1.101.0` 已在 Ubuntu 与 macOS 完成精确包兼容自动化验证，Ubuntu 另外完成带 PostgreSQL 的真实登录和 15 个核心 Admin UI 路由复核。macOS 不宣称完成同等范围的逐页人工检查。

安装器会复制 LiteLLM 自带静态 UI 到一个单独目录，然后注入翻译脚本。这样升级、校验
和回退都不会直接触碰 LiteLLM 安装包。

```zsh
git clone https://github.com/leonathan369-droid/litellm-ui-zh.git
cd litellm-ui-zh
python3 scripts/install.py install \
  --target "$HOME/.config/litellm/ui-zh"
python3 scripts/install.py check \
  --target "$HOME/.config/litellm/ui-zh"
```

然后在启动 LiteLLM 的服务环境中设置：

```zsh
export LITELLM_UI_PATH="$HOME/.config/litellm/ui-zh"
```

LiteLLM `1.101.0` 的 Ubuntu/macOS 真实包兼容检查均已通过；Ubuntu 还完成数据库支持的登录、15 个核心管理路由和人工截图复核。完整范围与平台差异见 <https://github.com/leonathan369-droid/litellm-ui-zh/blob/main/docs/compatibility.md>；Windows 与其他 LiteLLM 版本仍欢迎提交兼容性反馈。

这是社区补丁，不是 LiteLLM 官方发布。遇到未翻译文本、安装问题或升级兼容性问题，请
使用仓库 Issue 表单报告：<https://github.com/leonathan369-droid/litellm-ui-zh/issues>。
提交前请脱敏，绝不要发布 API Key、`MASTER_KEY`、数据库 URL、Cookie、完整配置或
未脱敏日志。

如果这个项目对你有帮助，欢迎点个 Star。

仓库地址：<https://github.com/leonathan369-droid/litellm-ui-zh>
