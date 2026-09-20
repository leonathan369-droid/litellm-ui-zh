# macOS setup

安装器不会修改 LaunchAgents、shell profile 或 LiteLLM 配置。

安装：

```zsh
python3 scripts/install.py install \
  --target "$HOME/.config/litellm/ui-zh"
```

LiteLLM 或本仓库升级后：

```zsh
python3 scripts/install.py upgrade \
  --target "$HOME/.config/litellm/ui-zh"
```

检查：

```zsh
python3 scripts/install.py check --target "$HOME/.config/litellm/ui-zh"
python3 scripts/install.py diagnose --target "$HOME/.config/litellm/ui-zh"
```

启动 LiteLLM 的同一环境中设置：

```zsh
export LITELLM_UI_PATH="$HOME/.config/litellm/ui-zh"
litellm --host 127.0.0.1 --port 4000
```

对于 launchd，把 `LITELLM_UI_PATH` 放到实际服务启动环境，而不是只放在交互 Shell。不要把密钥、数据库 URL 或完整生产配置写入本仓库或 shell history。

回到原始 WebUI 时移除 `LITELLM_UI_PATH` 并重启；也可以使用 `restore` 把自定义目录恢复成当前 LiteLLM 原始 UI，同时保留旧补丁备份。
