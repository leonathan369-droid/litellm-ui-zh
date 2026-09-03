# macOS setup

The installer deliberately does not modify LaunchAgents, shell profiles, or
LiteLLM configuration. After a successful install, set `LITELLM_UI_PATH` in
the same environment that starts LiteLLM:

```zsh
export LITELLM_UI_PATH="$HOME/.config/litellm/ui-zh"
litellm --host 127.0.0.1 --port 4000
```

For a `launchd` service, add the environment variable to the service's own
startup command, then reload or restart that service. Do not place API keys,
database URLs, or master keys in this repository or in shell history.

To return to the original WebUI, remove `LITELLM_UI_PATH` and restart LiteLLM.
`restore` is useful when you want the custom directory to contain a pristine
copy of the packaged UI while retaining the previous patched copy as a backup.
