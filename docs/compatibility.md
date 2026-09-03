# LiteLLM 版本兼容性记录

本页记录可复现的 LiteLLM WebUI 中文覆盖层验证结果，方便安装前判断风险。它不是
LiteLLM 官方兼容性承诺；未列出的系统、浏览器或版本均视为尚未验证。

## 状态说明

- `已验证`：维护者按本仓库安装、校验并在真实浏览器中检查过。
- `社区反馈`：由用户按完整模板报告，等待维护者复核。
- `排查中`：已有可复现问题，尚未确认根因或修复方案。
- `不兼容`：已确认当前版本无法正常使用，并附有可复现依据。

## 已验证记录

| LiteLLM 版本 | 系统 | 验证日期 | 状态 | 验证范围 |
| --- | --- | --- | --- | --- |
| 1.99.0 | macOS | 2026-09-03 | 已验证 | 安装器完成 51 个 HTML 路由注入；`check` 通过；真实浏览器加载中文覆盖层并手动检查常用管理界面。 |

## 升级前自测

升级 LiteLLM 后，先在单独的自定义 UI 目录重新安装并运行校验：

```zsh
python3 scripts/install.py install \
  --target "$HOME/.config/litellm/ui-zh"
python3 scripts/install.py check \
  --target "$HOME/.config/litellm/ui-zh"
```

随后让服务使用该目录并检查你实际会使用的 WebUI 路由。生产环境先在测试实例验证；
若需回退，移除 `LITELLM_UI_PATH` 后重启 LiteLLM，或使用 `restore` 恢复自定义目录。

## 提交兼容性反馈

升级成功、翻译异常或页面无法加载，都欢迎提交
[版本兼容性报告](https://github.com/leonathan369-droid/litellm-ui-zh/issues/new?template=compatibility.yml)。
报告请包含：原版本与目标版本、系统、浏览器、受影响路由、最短复现步骤，以及已脱敏的
诊断信息。

不要提交 API Key、`MASTER_KEY`、密码、Cookie、数据库 URL、完整配置、请求内容或未
脱敏日志。LiteLLM Proxy、Provider、数据库和上游 WebUI 的非翻译问题请提交至
[LiteLLM 上游 Issue](https://github.com/BerriAI/litellm/issues)。
